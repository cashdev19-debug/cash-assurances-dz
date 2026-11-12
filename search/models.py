from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from wagtail.models import Page, Locale,TranslatableMixin
from wagtail.documents import get_document_model
from wagtail.snippets.models import register_snippet
from django.db import models
from wagtail.admin.panels import FieldPanel,MultiFieldPanel,InlinePanel,FieldRowPanel
from wagtail.fields import RichTextField
from wagtail.contrib.settings.models import BaseGenericSetting,register_setting



Document = get_document_model()


@register_setting(icon="search")
class SearchPageText(BaseGenericSetting):
    subtitle =models.CharField(max_length=200)
    modal_search_placeholder = models.CharField(max_length=255,)
    modal_first_heading_text = models.CharField(max_length=255)
    modal_no_results_text = models.CharField(max_length=255)
    modal_view_all_text = models.CharField(max_length=255)
    search_placeholder = models.CharField(max_length=255)
    search_button_text = models.CharField(max_length=255)
    result_heading_text = models.CharField(max_length=200,null=True)
    first_heading_text = RichTextField(null=True)
    no_results_text = RichTextField(null=True)
    found_heading = models.CharField(max_length=255,)
    pages_title = models.CharField(max_length=255)
    documents_title = models.CharField(max_length=255)    

    panels = [
             MultiFieldPanel([
                FieldRowPanel([
                     FieldPanel("subtitle_fr"),
                     FieldPanel("subtitle_en"),
                     FieldPanel("subtitle_ar"),
                     ]),],"subtitle"),
             
             MultiFieldPanel([
                FieldRowPanel([
                     FieldPanel("modal_search_placeholder_fr"),
                     FieldPanel("modal_search_placeholder_en"),
                     FieldPanel("modal_search_placeholder_ar"),
                     ]),],"Modal search placeholder"),
             
             MultiFieldPanel([
                FieldRowPanel([
                     FieldPanel("modal_first_heading_text_fr"),
                     FieldPanel("modal_first_heading_text_en"),
                     FieldPanel("modal_first_heading_text_ar"),
                     ]),],"Modal first heading text"),
             
             MultiFieldPanel([
                FieldRowPanel([
                     FieldPanel("modal_no_results_text_fr"),
                     FieldPanel("modal_no_results_text_en"),
                     FieldPanel("modal_no_results_text_ar"),
                     ]),],"Modal no results text"),
             
             MultiFieldPanel([
                FieldRowPanel([
                     FieldPanel("modal_view_all_text_fr"),
                     FieldPanel("modal_view_all_text_en"),
                     FieldPanel("modal_view_all_text_ar"),
                     ]),],"Modal view all text"),
             
             MultiFieldPanel([
                FieldRowPanel([
                    FieldPanel("search_placeholder_fr"),
                    FieldPanel("search_placeholder_en"),
                    FieldPanel("search_placeholder_ar"),
                         ]),],"Search placeholder"),
             MultiFieldPanel([
                FieldRowPanel([
                    FieldPanel("search_button_text_fr"),
                    FieldPanel("search_button_text_en"),
                    FieldPanel("search_button_text_ar"),
                    ]),],"Search button text"),
             MultiFieldPanel([
                                 FieldRowPanel([
            FieldPanel("result_heading_text_fr"),
            FieldPanel("result_heading_text_en"),
            FieldPanel("result_heading_text_ar"),
             ])],"Result heading text"),
             MultiFieldPanel([
                                 FieldRowPanel([                  
            FieldPanel("first_heading_text_fr"),
            FieldPanel("first_heading_text_en"),
            FieldPanel("first_heading_text_ar"),
                                           ]),],"First heading text"),
             MultiFieldPanel([
                                 FieldRowPanel([
            FieldPanel("no_results_text_fr"),
            FieldPanel("no_results_text_en"),
            FieldPanel("no_results_text_ar"),
             ]),],"No results text"),
             MultiFieldPanel([
                                 FieldRowPanel([
            FieldPanel("found_heading_fr"),
            FieldPanel("found_heading_en"),
            FieldPanel("found_heading_ar"),
             ]),],"Found heading"),
             MultiFieldPanel([
                                 FieldRowPanel([
            FieldPanel("pages_title_fr"),
            FieldPanel("pages_title_en"),
            FieldPanel("pages_title_ar"),
             ]),],"Pages title"),
             MultiFieldPanel([
                                 FieldRowPanel([
            FieldPanel("documents_title_fr"),
            FieldPanel("documents_title_en"),
            FieldPanel("documents_title_ar"),
             ])],"Documents title"),
        ]

    class Meta:
        verbose_name = "Search Page Text"
        verbose_name_plural = "Search Page Texts"

    def __str__(self):
        return f"Search Page Texts "
    
