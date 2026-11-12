from django.db import models
from django.db import models
from django.core.files.storage import default_storage
from modelcluster.fields import ParentalKey

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.forms.models import (
    AbstractForm, 
    AbstractFormField, 
    FORM_FIELD_CHOICES
)
from wagtail.contrib.forms.forms import FormBuilder
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render
from base.models import Wilaya 
from wagtail.contrib.forms.views import SubmissionsListView
from django.utils.html import format_html
from wagtail.contrib.forms.models import AbstractFormSubmission
from wagtail.models import TranslatableMixin

from django.utils.translation import gettext_lazy as _

class RecruitmentSubmissionsListView(SubmissionsListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Don't touch CSV/XLSX exports
        if self.is_export:
            return context

        # Real column order as rendered in the table
        column_names = [name for name, label in self.form_page.get_data_fields()]
        file_field_names = {
            f.clean_name
            for f in self.form_page.get_form_fields()
            if f.field_type == "file"
        }

        submissions = context[self.context_object_name]

        for submission, row in zip(submissions, context["data_rows"]):
            form_data = submission.get_data()

            for idx, name in enumerate(column_names):
                if name not in file_field_names:
                    continue

                file_path = form_data.get(name)
                if not file_path:
                    continue

                # If it's already a full URL, use it as is
                if str(file_path).startswith(("http://", "https://", "/")):
                    file_url = file_path
                else:
                    file_url = default_storage.url(file_path)

                row["fields"][idx] = format_html(
                    '<a href="{}" target="_blank" rel="noopener" class="button button-small button-secondary">'
                    "Download CV</a>",
                    file_url,
                )

        return context

class CustomFormBuilder(FormBuilder):
    def create_phone_field(self, field, options):
        widget = forms.TextInput(attrs={
            'type': 'tel',
            'data-field-type': 'phone' # Marker for identification
        })
        return forms.CharField(widget=widget, **options)
    
    def create_file_field(self, field, options):
        def validate_resume(uploaded_file):
            valid_mime_types = [
                'application/pdf', 
                'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            if uploaded_file.content_type not in valid_mime_types:
                raise ValidationError("Invalid file type. Only PDF and Word documents are permitted.")

            if uploaded_file.size > 5 * 1024 * 1024:
                raise ValidationError("File size exceeds the 5MB limit.")

        # Attach validator to options
        options['validators'] = options.get('validators', []) + [validate_resume]
        return forms.FileField(**options)
    
    def create_wilaya_field(self, field, options):
        """Dynamically fetch all Wilayas from the snippet and populate choices."""
        wilayas = Wilaya.objects.all()
        choices = [('', options['help_text'])] + [(w.nom, str(w)) for w in wilayas]
        options['choices'] = choices
        return forms.ChoiceField(**options)

    def get_create_field_function(self, type):
        if type == 'file':
            create_field_function = self.create_file_field
        elif type == 'wilaya':
            create_field_function = self.create_wilaya_field
        else:
            create_field_function = super().get_create_field_function(type)

        def wrapped_create_field_function(field, options):
            created_field = create_field_function(field, options)
            if hasattr(field, 'class_div') and field.class_div:
                created_field.widget.attrs.update({"class_div": field.class_div})
            return created_field

        return wrapped_create_field_function

class RecruitmentField(TranslatableMixin,AbstractFormField):
    page = ParentalKey(
        'RecruitmentPage', 
        on_delete=models.CASCADE, 
        related_name='custom_form_fields'
    )

    CUSTOM_FIELD_CHOICES = list(FORM_FIELD_CHOICES) + [
        ('phone', 'Phone Number'),
        ('file', 'File Upload'),
        ('wilaya', 'Wilaya Select'),
    ]

    field_type = models.CharField(
        verbose_name='field type',
        max_length=16,
        choices=CUSTOM_FIELD_CHOICES,
    )

    class_div = models.CharField(max_length=255, blank=True)

class RecruitmentPage(AbstractForm):
    form_builder = CustomFormBuilder
    submissions_list_view_class = RecruitmentSubmissionsListView
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Image de couverture de la page"
    )

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)
    button_text=models.CharField(max_length=60,null=True)
    content_panels = AbstractForm.content_panels + [
        FieldPanel('cover_image'),
        FieldPanel('intro'),
        InlinePanel('custom_form_fields', label="Champs du formulaire"),
        FieldPanel('button_text'),
        FieldPanel('thank_you_text'),
    ]


    
    def serve(self, request, *args, **kwargs):
        if request.method == 'POST' and request.headers.get('HX-Request'):
            form = self.get_form(request.POST, request.FILES, page=self, user=request.user)
            if form.is_valid():
                self.process_form_submission(form)
                return render(request, "recruitment/recruitment_page.html#result", {
                    'page': self,
                    'thank_you_text': self.thank_you_text,
                })
            else:
                # Return the form fragment with field validation errors attached
                return render(request, "recruitment/recruitment_page.html#form", {
                    'page': self,
                    'form': form,
                })
        if request.method == 'GET' and request.headers.get('HX-Request'):
            form = self.get_form(page=self, user=request.user)
            return render(request, "recruitment/recruitment_page.html#form", {
                'page': self,
                'form': form,
            })
        # 2. Standard GET request (returns full page layout)
        return super().serve(request, *args, **kwargs)
    
    def get_form_fields(self):
        return self.custom_form_fields.all()


    def get_form_class(self):
        form_class = super().get_form_class()
        page_instance = self

        class UniqueValidatedForm(form_class):
            def clean(self):
                cleaned_data = super().clean()

                # 1. Algerian Phone Validation for any field set to 'phone'
                phone_field_names = [
                    f.clean_name for f in page_instance.get_form_fields() 
                    if f.field_type == 'phone'
                ]
                
                algeria_regex = r"^(\+213|00213|0)[1-9]\d{8}$"

                for field_name in phone_field_names:
                    phone_value = cleaned_data.get(field_name)
                    if phone_value:
                        # Strip spaces, dashes, dots, and parentheses
                        stripped_phone = re.sub(r'[\s\-\.\(\)]', '', phone_value)
                        
                        if not re.match(algeria_regex, stripped_phone):
                            self.add_error(
                                field_name,
                                ValidationError("Veuillez saisir un numéro de téléphone algérien valide (ex: 0550123456 ou +213550123456).")
                            )

                return cleaned_data

        return UniqueValidatedForm

    def process_form_submission(self, form):

        for field in self.get_form_fields():
            if field.field_type == 'file':
                uploaded_file = form.cleaned_data.get(field.clean_name)
                if uploaded_file and hasattr(uploaded_file, 'name'):
                    saved_path = default_storage.save(
                        f"uploads/resumes/{uploaded_file.name}", 
                        uploaded_file
                    )
                    form.cleaned_data[field.clean_name] = saved_path

        return super().process_form_submission(form)    
    
    
    
    
    
    
    
    
    
    
    