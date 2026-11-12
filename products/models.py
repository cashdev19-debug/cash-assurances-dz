
from wagtail.snippets.models import register_snippet
from django.db import models
from wagtail.models import Page,TranslatableMixin
from wagtail.fields import RichTextField
from .blocks import *

from wagtail.admin.panels import (FieldPanel)
from wagtail_localize.fields import SynchronizedField
from modelcluster.models import ClusterableModel
from django.utils.text import slugify
from wagtail_localize.fields import TranslatableField, SynchronizedField
from wagtail.fields import StreamField



@register_snippet
class ProductCategory(TranslatableMixin):
    name = models.CharField(max_length=255)
    slug = models.SlugField(null=True,max_length=200)  
    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]
    def __str__(self):
        return self.name
    class Meta(TranslatableMixin.Meta):
        verbose_name="Catergory"
        verbose_name_plural="Catergories"

@register_snippet
class Product(ClusterableModel,TranslatableMixin):
    image =  models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,null=True)
    description = RichTextField()
    garanties = RichTextField()
    product_category = models.ForeignKey(ProductCategory,on_delete=models.CASCADE,null=True)
    panels = [
        FieldPanel('product_category'),
        FieldPanel('image'),
        FieldPanel('title'),    
        FieldPanel('slug'),    
        FieldPanel('description'),
        FieldPanel('garanties'),
    ]
    translatable_fields = [
        SynchronizedField("image"),
        TranslatableField("title"),
        TranslatableField("slug"),
        TranslatableField("description"),
        TranslatableField("garanties"),
    ]
    def __str__(self):
        return self.title
    class Meta(TranslatableMixin.Meta):
        verbose_name="Product"
        verbose_name_plural="Products"


    
class ProductsPage(Page):
        subtitle =models.CharField(max_length=200)
        sections = StreamField(
            [   
             ("OneProductBlock", oneProductBlock()),  
             ("MultipleProducstBlock", multipleProducstBlock()),  
            ],
            use_json_field=True,    
            blank=True,
            default=[],
        )
        content_panels = Page.content_panels + [
            FieldPanel("subtitle"),
            FieldPanel("sections"),
        ]
    
   
class ProductDetail(Page):
        subtitle =models.CharField(max_length=200)
        button_text =models.CharField(max_length=100,null=True)
        button_link =models.ForeignKey(
                        'wagtailcore.Page',
                        null=True,
                        blank=True,
                        on_delete=models.SET_NULL,
                        related_name='+',
                                        )
        cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )        
        description = RichTextField(null=True)
        garanties = RichTextField(null=True)
        content_panels = Page.content_panels + [
            FieldPanel("subtitle"),
            FieldPanel("button_text"),
            FieldPanel("button_link"),
            FieldPanel("cover_image"),
            FieldPanel("description"),
            FieldPanel("garanties"),
        ]
        
        def get_context(self, request):
            context = super().get_context(request)
            parent_page = self.get_parent()
            queryset = ( ProductDetail.objects.child_of(parent_page)
                    .live()
                    .public()
                    .not_page(self)
                    .distinct()
                )
            sorted_posts  = sorted(
                    list(queryset), 
                    key=lambda x: x.id , 
                    reverse=True
                )
            context['related_products'] = sorted_posts[:3]
            return context
        
    
    

