from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.fields import StreamField
from django.utils.translation import gettext_lazy as _
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
from django.db.models import Q

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

from django.utils.translation import get_language

VALIDATION_ERRORS = {
    "phone": {
        "invalid_algerian": {
            "fr": "Veuillez entrer un numéro de téléphone algérien valide (ex: 0550123456 ou +213550123456).",
            "en": "Please enter a valid Algerian phone number (e.g., 0550123456 or +213550123456).",
            "ar": "يرجى إدخال رقم هاتف جزائري صالح (مثل: 0550123456 أو +213550123456)."
        }
    },
    "email": {
        "already_registered": {
            "fr": "Cette adresse e-mail est déjà enregistrée.",
            "en": "This email address has already been registered.",
            "ar": "عنوان البريد الإلكتروني هذا مسجل بالفعل."
        }
    }
}
def get_error_message(field_type, error_key, lang=None):
    lang = (lang or get_language() or "fr").split("-")[0]
    error_dict = VALIDATION_ERRORS.get(field_type, {}).get(error_key, {})
    return error_dict.get(
        lang, error_dict.get("fr", error_dict.get("en", "Une erreur s'est produite."))
    )
class FormPage(AbstractForm):
    form_type = models.CharField(
        max_length=50, null=True,
        choices={"Contact": "Contact", "Newsletter": "Newsletter"},
    )
    form_builder = CustomFormBuilder
    button_text = models.CharField(max_length=50, null=True)
    thank_you_text = RichTextField(blank=True)

    # Editable error messages (empty = use the default text)
    phone_error_message = models.CharField(
        "message d'erreur numéro de téléphone invalide", max_length=255, blank=True,
        help_text="S'affiche lorsque le numéro de téléphone n'est pas un numéro algérien valide.  "
                  "Laissez vide pour utiliser le texte par défaut.",
    )
    email_exists_error_message = models.CharField(
        "Message indiquant que l’adresse e-mail est déjà enregistrée", max_length=255, blank=True,
        help_text="Formulaires de newsletter uniquement. S’affiche lorsque l’adresse e-mail est déjà enregistrée. "
                  "Laissez vide pour utiliser le texte par défaut.",
    )

    content_panels = AbstractForm.content_panels + [
        FieldPanel("form_type"),
        InlinePanel("form_fields"),
        FieldPanel("button_text"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldPanel("phone_error_message"),
                FieldPanel("email_exists_error_message"),
            ],
            heading="Error messages",
        ),
    ]

    def serve(self, request, *args, **kwargs):
        current_lang = get_language() or "fr"
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
                        {"self": self, "form": form, "LANGUAGE_CODE": current_lang},
                    )
                return self.render_landing_page(
                    request, form_submission=form_submission, *args, **kwargs
                )
            else:
                if request.headers.get("HX-Request"):
                    return render(
                        request,
                        "home/partials/contact_form_partial.html",
                        {"self": self, "form": form, "LANGUAGE_CODE": current_lang},
                    )
        else:
            form = self.get_form(page=self, user=request.user)
        context = self.get_context(request)
        context["form"] = form
        return render(request, self.get_template(request), context)

    # ---------- messages ----------
    def get_message(self, field_type, error_key):
        custom = {
            ("phone", "invalid_algerian"): self.phone_error_message,
            ("email", "already_registered"): self.email_exists_error_message,
        }.get((field_type, error_key))
        return custom or get_error_message(
            field_type, error_key, lang=self.locale.language_code
        )

    # ---------- duplicate email check ----------
    def email_already_registered(self, value):
        pages = type(self).objects.filter(
            translation_key=self.translation_key
        ).prefetch_related("form_fields")

        query = Q()
        for page in pages:
            for field in page.form_fields.all():
                if field.field_type == "email":
                    query |= Q(**{f"form_data__{field.clean_name}__iexact": value})
        if not query:
            return False
        return FormSubmission.objects.filter(page__in=pages).filter(query).exists()

    def get_form_class(self):
        form_class = super().get_form_class()
        page = self

        fields = list(page.form_fields.all())
        phone_names = [f.clean_name for f in fields if f.field_type == "phone"]
        email_names = [f.clean_name for f in fields if f.field_type == "email"]
        is_newsletter = page.form_type == "Newsletter"
        algeria_regex = re.compile(r"^(\+213|00213|0)[1-9]\d{8}$")

        class UniqueValidatedForm(form_class):
            def clean(self):
                cleaned_data = super().clean()

                for name in phone_names:
                    value = cleaned_data.get(name)
                    if value and not algeria_regex.match(re.sub(r"[\s\-\.\(\)]", "", value)):
                        self.add_error(
                            name,
                            ValidationError(page.get_message("phone", "invalid_algerian")),
                        )

                if is_newsletter:
                    for name in email_names:
                        value = cleaned_data.get(name)
                        if value and page.email_already_registered(value):
                            self.add_error(
                                name,
                                ValidationError(page.get_message("email", "already_registered")),
                            )
                            break

                return cleaned_data

        return UniqueValidatedForm
    
    
   