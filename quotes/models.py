from django.db import models
from wagtail.models import Page
from .blocks import *
from wagtail.admin.panels import (
    FieldPanel, 
)
from wagtail.fields import StreamField
from django.shortcuts import render
    
class QuotesPage(Page):
    subtitle =models.CharField(max_length=100)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
   
    content_panels = Page.content_panels + [
            FieldPanel("subtitle"),
            FieldPanel("cover_image"),
   
        ]


# home/models.py
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.cache import patch_vary_headers
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.forms.models import FormSubmission
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail_flexible_forms import blocks as wff_blocks
from wagtail_flexible_forms.models import (
    AbstractSessionFormSubmission,
    AbstractSubmissionRevision,
    StreamFormMixin,
)


# ---------------------------------------------------------------------------
# 1. Blocks (you already have these; shown for completeness)
# ---------------------------------------------------------------------------
STREAMFORM_FIELDS = wff_blocks.FormFieldsBlock()  # or your own StreamBlock
# If you mix content blocks between fields, build your own list like:
# STREAMFORM_FIELDS = wff_blocks.FormFieldsBlock([("heading", blocks.CharBlock()), ...])

STREAMFORM_STEP_BLOCKS = [
    ("sf_step", wff_blocks.FormStepBlock([("form_fields", STREAMFORM_FIELDS)])),
]


# ---------------------------------------------------------------------------
# 2. Session (temporary) submission models (you already have these)
# ---------------------------------------------------------------------------



class SessionFormSubmission(AbstractSessionFormSubmission):
    form_data = models.TextField(default="[]")

    @staticmethod
    def get_revision_class():
        return SubmissionRevision   # defined below it, or import lazily


class SubmissionRevision(AbstractSubmissionRevision):
    pass



class SubmissionRevision(AbstractSubmissionRevision):
    pass


# ---------------------------------------------------------------------------
# 3. HTMX helper
# ---------------------------------------------------------------------------
def is_htmx(request):
    # "HX-Boosted" requests expect a full page, so exclude them.
    return (
        request.headers.get("HX-Request") == "true"
        and request.headers.get("HX-Boosted") != "true"
    )


class MultiStepFormPageQuote(StreamFormMixin, Page):
    # Full-page templates (normal browser load / refresh / no-JS fallback)
    template = "quotes/multistep_form_page.html"
    landing_page_template = "quotes/multistep_form_landing.html"

    # Fragments returned to HTMX requests
    htmx_step_template = "quotes/partials/_step_response.html"
    htmx_landing_template = "quotes/partials/_landing_response.html"

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(
        blank=True, help_text="Shown after the last step is submitted."
    )
    # Optional: redirect to a real Wagtail page instead of showing the text above
    landing_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional. If set, users are sent to this page after the last step.",
    )

    form_fields = StreamField(STREAMFORM_STEP_BLOCKS, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("form_fields"),
        FieldPanel("thank_you_text"),
        FieldPanel("landing_page"),
    ]

    @staticmethod
    def get_submission_class():
        return FormSubmission

    @staticmethod
    def get_session_submission_class():
        return SessionFormSubmission


    def get_submissions(self):
        return self.get_submission_class()._default_manager.filter(page=self)
    # -- unsaved pages (e.g. admin preview of a page you haven't saved yet) --
    def get_session_submission(self, request):
        # The package runs Submission.objects.filter(page=self), which raises
        # "Model instances passed to related filters must be saved" when the
        # page has no pk yet. Return a throw-away, unsaved submission instead.
        if self.pk is None:
            Submission = self.get_session_submission_class()
            return Submission(form_data="[]")
        return super().get_session_submission(request)

    # -- choose full page vs fragment ------------------------------------
    def get_template(self, request, *args, **kwargs):
        if is_htmx(request):
            return self.htmx_step_template
        return super().get_template(request, *args, **kwargs)

    def get_landing_page_template(self, request, *args, **kwargs):
        if is_htmx(request):
            return self.htmx_landing_template
        return super().get_landing_page_template(request, *args, **kwargs)

    # -- after the last step ---------------------------------------------
    def render_landing_page(self, request, form_submission=None, *args, **kwargs):
        if self.landing_page_id:
            url = self.landing_page.specific.url
            if is_htmx(request):
                # Tells HTMX to do a full browser redirect
                response = HttpResponse(status=204)
                response["HX-Redirect"] = url
                return response
            return HttpResponseRedirect(url)
        return super().render_landing_page(request, form_submission, *args, **kwargs)

    def serve(self, request, *args, **kwargs):
        # Base serve():
        #   * valid POST, not last step -> 302 to self.url (HTMX follows it and
        #     swaps in the next step, since the GET carries HX-Request too)
        #   * invalid POST             -> re-renders current step with errors
        #   * last step                -> render_landing_page()
        response = super().serve(request, *args, **kwargs)
        # Same URL returns different HTML for HTMX vs normal requests
        patch_vary_headers(response, ["HX-Request"])
        return response
    
    
    