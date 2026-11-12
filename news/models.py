
from wagtail.snippets.models import register_snippet
from django.db import models

from wagtail.models import Page,Locale,Orderable,TranslatableMixin
from wagtail.fields import RichTextField

from .blocks import *
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,HelpPanel 
)

from modelcluster.fields import ParentalKey

from wagtail.fields import StreamField
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalManyToManyField
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from wagtail_localize.fields import TranslatableField, SynchronizedField


@register_snippet
class NewsCategory(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        help_text="A unique URL-friendly identifier, auto-generated from the name."
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'), 
    ]
    translatable_fields = [
            TranslatableField("name"),
            SynchronizedField("slug"),
          
        ]

    def __str__(self):
        return self.name
    

    
class NewsPage(Page):
    subtitle =models.CharField(max_length=200)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    empty_filter_text = models.CharField(max_length=200,null=True)        
    pagination_options = StreamField([
                        ("pagination", PaginationStructBlock()),
                        ], max_num=1,use_json_field=True,blank=True,default=[])
    sidebar_sections = StreamField([
                        ("category",CategoryBlock(),),
                        ("NewsLetter",NewsLetterBlock()),],use_json_field=True,blank=True,default=[])
    article_recents_number = models.PositiveIntegerField(default=3)
    content_panels = Page.content_panels + [
            FieldPanel("subtitle"),
            FieldPanel("cover_image"),
            FieldPanel("empty_filter_text"),
            FieldPanel("sidebar_sections"),
            FieldPanel("pagination_options"),
            FieldPanel("article_recents_number",),
            HelpPanel("Le nombre d'articles récents sur la page de détail d'un article")
            
        ]
    def get_context(self, request):
        locale = self.locale
        context = super().get_context(request)
        all_news =NewsDetail.objects.child_of(self).live().order_by("date")
        total_all_news = all_news.count()
        selected_category_slug = request.GET.get("category")
        selected_category = None
        if selected_category_slug:
            selected_category = get_object_or_404(NewsCategory, slug=selected_category_slug,locale=locale)
            all_news = all_news.filter(category=selected_category,locale=locale).distinct()
        paginator = Paginator(all_news, 5)
        page_request = request.GET.get("page")
        try:
            news = paginator.get_page(page_request)
        except PageNotAnInteger:
            news = paginator.page(1)
        except EmptyPage:
            news = paginator.page(paginator.num_pages)    
        page_range = paginator.get_elided_page_range(
            number=news.number,
            on_each_side=1,  
            on_ends=1        
        )
        context['page_range'] = page_range 
        context['news'] = news 
        context['total_all_news'] = total_all_news 
        context['categories'] = NewsCategory.objects.filter(locale=locale).annotate(total_articles=Count("news_detail__id",filter=Q(news_detail__live=True,news_detail__locale=locale),distinct=True  ))
        context["selected_category"] = selected_category
        return context
    
    
    

class CarouselImage(Orderable):
        page = ParentalKey('NewsDetail', related_name='carousel_images', on_delete=models.CASCADE)
        image = models.ForeignKey(
            'wagtailimages.Image',
            on_delete=models.CASCADE,
            related_name='+'
        )
        caption = models.CharField(blank=True, max_length=250)
        panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]
class NewsDetail(Page):
    subtitle =models.CharField(max_length=200)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )        
    text = RichTextField(null=True,features=["h2","h3","h4","bold","italic","ol","ul","hr","link","document-link","blockquote","superscript","subscript","strikethrough"])
    date = models.DateField(null=True)
    category = models.ForeignKey('news.NewsCategory',related_name= 'news_detail', null=True,blank=True,on_delete=models.PROTECT)
    content_panels = Page.content_panels + [
            FieldPanel("subtitle"),
            FieldPanel("category" ),
            FieldPanel("date"),
            FieldPanel("cover_image"),
            FieldPanel("text"),
            InlinePanel('carousel_images', label="Carousel Images"),
        ]
   
    def get_context(self, request):
        context = super().get_context(request)
        parent_page = self.get_parent()
        limit = parent_page.article_recents_number or 3
        queryset = (
            NewsDetail.objects.child_of(parent_page)
            .live()
            .public()
            .not_page(self)
            .distinct()
        )
        related = (
                NewsDetail.objects.child_of(self.get_parent())
                .live().public().not_page(self)
                .order_by("-date", "-first_published_at")[:limit]
        )
        context["related_posts"] = related
        return context
    class Meta:
        verbose_name = "News article"
        verbose_name_plural = "News article"
