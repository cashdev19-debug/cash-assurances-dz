from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.fields import StreamField

# import MultiFieldPanel:
from .blocks import (
    CarouselBlock,
    DevisBlock,
    ProduitBlock,
    TemoignageBlock,
    RecrutementBlock,
    contactBlock,
    newsletterBlock,
    mobile_block,
    faq_block,
    annualReport_block,
)
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import (
    AbstractEmailForm,
    AbstractFormField,
    FormBuilder,
    AbstractForm,
)
from modelcluster.fields import ParentalKey
from wagtail.models import TranslatableMixin
from django.core.validators import RegexValidator
import re
from django.shortcuts import render

from django.core.exceptions import ValidationError
from wagtail.contrib.forms.models import (AbstractForm, AbstractFormField, FormSubmission,FORM_FIELD_CHOICES)
from django import forms


class HomePage(Page):
    sections = StreamField(
        [
            ("Slides", CarouselBlock()),
            ("Devis", DevisBlock()),
            ("Produit", ProduitBlock()),
            ("Temoignage", TemoignageBlock()),
            ("Recrutement", RecrutementBlock()),
            ("Faq", faq_block()),
            ("Annual_report", annualReport_block()),
            ("Contact_form1", contactBlock()),
            ("Newsletter", newsletterBlock()),
            ("Mobile", mobile_block()),
        ],
        use_json_field=True,
        blank=True,
        default=[],
    )
    content_panels = Page.content_panels + [
        FieldPanel("sections"),
    ]


class FormField(TranslatableMixin,AbstractFormField):
    page = ParentalKey("FormPage", on_delete=models.CASCADE, related_name="form_fields")
    
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
    class_div = models.CharField(
        max_length=255,
        blank=True,
        choices={
            "col-span-2": "100%",
            "col-span-1": "50%",
        },
    )
    panels = AbstractFormField.panels + [
        FieldPanel("class_div"),
    ]


class CustomFormBuilder(FormBuilder):
    def create_phone_field(self, field, options):
        widget = forms.TextInput(attrs={
            'type': 'tel',
            'data-field-type': 'phone' # Marker for identification
        })
        return forms.CharField(widget=widget, **options)

    def get_create_field_function(self, type):
        create_field_function = super().get_create_field_function(type)

        def wrapped_create_field_function(field, options):
            created_field = create_field_function(field, options)
            created_field.widget.attrs.update({"class_div": field.class_div})
            return created_field

        return wrapped_create_field_function



class FormPage(AbstractForm):
    form_type = models.CharField(max_length=50,null=True,choices={"Contact":"Contact","Newsletter":"Newsletter"})
    form_builder = CustomFormBuilder
    button_text = models.CharField(max_length=50, null=True)
    thank_you_text = RichTextField(blank=True)
    content_panels = AbstractForm.content_panels + [
         FieldPanel("form_type"),
        InlinePanel("form_fields"),
        FieldPanel("button_text"),
        FieldPanel("thank_you_text"),
    ]
    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            form = self.get_form(
                request.POST, request.FILES, page=self, user=request.user
            )
            if form.is_valid():
                form_submission = self.process_form_submission(form)
                if request.headers.get("HX-Request"):
                    return render(
                        request,
                        "home/partials/contact_form_partial.html",
                        {"self": self, "form": form},
                    )
                return self.render_landing_page(
                    request, form_submission=form_submission, *args, **kwargs
                )
            else:
                if request.headers.get("HX-Request"):
                    return render(
                        request,
                        "home/partials/contact_form_partial.html",
                        {"self": self, "form": form},
                    )
        else:
            form = self.get_form(page=self, user=request.user)
        context = self.get_context(request)
        context["form"] = form
        return render(request, self.get_template(request), context)
    def get_form_class(self):
        form_class = super().get_form_class()
        page_instance = self

        class UniqueValidatedForm(form_class):
            def clean(self):
                cleaned_data = super().clean()
                phone_field_names = [
                f.clean_name for f in page_instance.form_fields.all() 
                if f.field_type == 'phone'
                ]
            
                algeria_regex = r"^(\+213|00213|0)[1-9]\d{8}$"
            
                for field_name in phone_field_names:
                    phone_value = cleaned_data.get(field_name)
                    if phone_value:
                    # Strip out common separators (spaces, dashes, dots, parentheses)
                        stripped_phone = re.sub(r'[\s\-\.\(\)]', '', phone_value)
                    
                        if not re.match(algeria_regex, stripped_phone):
                            self.add_error(
                            field_name,
                            ValidationError("Please enter a valid Algerian phone number (e.g., 0550123456 or +213550123456).")
                            )
                field_to_check = "email"
                user_value = cleaned_data.get(field_to_check)
                if user_value:
                    if page_instance.form_type == 'newsletter' or page_instance.__class__.__name__ == 'NewsletterPage':
                        submissions = FormSubmission.objects.filter(page=page_instance)
                        for sub in submissions:
                            data = sub.get_data()
                            if data.get(field_to_check) == user_value:
                                self.add_error(
                                    field_to_check,
                                    ValidationError(
                                        "This email address has already been registered."
                                    ),
                                )
                                break
                    elif page_instance.form_type == 'contact':
                        pass
                    return cleaned_data

        return UniqueValidatedForm
    
    
   