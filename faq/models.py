
from wagtail.snippets.models import register_snippet
from django.db import models
from wagtail.models import Page
from .blocks import *
from wagtail.admin.panels import (
    FieldPanel, 
)
from wagtail.fields import StreamField
from django.shortcuts import render
    
class FaqPage(Page):
    subtitle =models.CharField(max_length=100)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    faq_categories = StreamField([
                         ("documents_tab",CategoryFaqsBlock()),
                        ],use_json_field=True,blank=True,default=[])
    content_panels = Page.content_panels + [
            FieldPanel("subtitle"),
            FieldPanel("cover_image"),
            FieldPanel("faq_categories"),
        ]
        
    
