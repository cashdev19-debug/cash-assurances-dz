from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.fields import StreamField
# import MultiFieldPanel:
from .blocks import *
from wagtail.admin.panels import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel
)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField,FormBuilder
from modelcluster.fields import ParentalKey




class aboutPage(Page):
    pages_sections = StreamField([
                        ("Presentation",PresentationBlock()),
                        ("Timeline",TimelineBlock()),
                        ("Points_repere",PointsRepereBlock()),
                        ("CounterBlock",CounterBlock()),
                        ("StatsCard",StatsCardBlock()),
                        ("HumainCapital",HumainCapitalBlock()),
                       ],use_json_field=True,blank=True,default=[])
    content_panels = Page.content_panels + [
        FieldPanel('pages_sections'),
    ]
