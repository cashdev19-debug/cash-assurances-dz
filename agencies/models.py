
from wagtail.snippets.models import register_snippet
from django.db import models

from wagtail.models import Page,Orderable,TranslatableMixin
from wagtail.fields import RichTextField

from wagtail.snippets.views.snippets import EditView
# import MultiFieldPanel:
from .blocks import *
from wagtail.admin.panels import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel 
)
from wagtail_localize.fields import SynchronizedField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from django.utils.text import slugify
from wagtail_localize.fields import TranslatableField, SynchronizedField
from wagtail.fields import StreamField
from base.models import Agence,Wilaya,AgenceContact
from django.shortcuts import render
from wagtail.models import Locale
class AgenciesPage(Page):
    subtitle =models.CharField(max_length=100)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    title_form = models.CharField(max_length=100,null=True)        
    title_wilaya = models.CharField(max_length=100,null=True)        
    title_agence = models.CharField(max_length=100,null=True)        
    title_swilaya = models.CharField(max_length=100,null=True)        
    title_sagence = models.CharField(max_length=100,null=True)        
    title_details = models.CharField(max_length=100,null=True)     
    text_empty_details = models.CharField(max_length=100,null=True)   
    label_responsable = models.CharField(max_length=100,null=True)        
    label_email = models.CharField(max_length=100,null=True)        
    label_adresse = models.CharField(max_length=100,null=True)        
    label_fix = models.CharField(max_length=100,null=True)        
    label_fax = models.CharField(max_length=100,null=True)        
    label_mobile = models.CharField(max_length=100,null=True)        
    content_panels = Page.content_panels + [
            FieldPanel("subtitle"),
            FieldPanel("cover_image"),
            FieldPanel("title_form"),
            FieldPanel("title_wilaya"),
            FieldPanel("title_agence"),
            FieldPanel("title_swilaya"),
            FieldPanel("title_sagence"),
            FieldPanel("title_details"),
            FieldPanel("text_empty_details"),
            FieldPanel("label_responsable"),
            FieldPanel("label_email"),
            FieldPanel("label_adresse"),
            FieldPanel("label_fix"),
            FieldPanel("label_fax"),
            FieldPanel("label_mobile"),
           
        ]
    def get_context(self, request):
        context = super().get_context(request)
        context['wilayas'] = Wilaya.objects.filter(agence__isnull=False).distinct()
        context['agences'] = Agence.objects.all()
        return context
    def serve(self, request):  
        if request.headers.get('HX-Request') and 'agence_code' in request.GET:
            agence_code = request.GET.get('agence_code')
            agence = Agence.objects.get(code=agence_code) if agence_code else []
            agenceInfos = AgenceContact.objects.filter(page=agence.id)
            fix = agenceInfos.filter(contact_type="FIX")
            fax = agenceInfos.filter(contact_type="FAX")
            mobile = agenceInfos.filter(contact_type="MOBILE")
            email = agenceInfos.filter(contact_type="EMAIL")
            
            return render(request, 'agencies/partials/agence_infos.html', {
                'agence': agence,
                'fixs': fix,
                'faxs': fax,
                'mobiles': mobile,
                'emails': email,
                'label_responsable' :self.label_responsable,        
                'label_email' : self.label_email,        
                'label_adresse':self.label_adresse,        
                'label_fix':self.label_fix ,        
                'label_fax':self.label_fax,         
                'label_mobile':self.label_mobile  
            })
        if request.headers.get('HX-Request') and 'wilaya_code' in request.GET:
            wilaya_code = request.GET.get('wilaya_code')
          
            agences = Agence.objects.filter(wilaya__code=wilaya_code) if wilaya_code else []
            return render(request, 'agencies/partials/agence_select.html', {
                'agences': agences
            })
        
        return super().serve(request)