from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,InlinePanel,FieldRowPanel
)
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)
from wagtail.snippets.models import register_snippet
from wagtail.models import Page,Orderable,TranslatableMixin
from wagtail.fields import RichTextField
from wagtail_localize.fields import TranslatableField, SynchronizedField
from wagtail.fields import StreamField
from .blocks import *
from modeltranslation.translator import TranslationOptions




@register_setting(icon="warning")
class loi_18_07_consentement(BaseGenericSetting):
    active = models.BooleanField(default=True)
    cookie_age = models.IntegerField(null=True ,help_text="En seconds")
    title =models.CharField(max_length=100,null=True)
    text  = RichTextField()
    read_button_text = models.CharField(max_length=100)
    decline_button_text = models.CharField(max_length=100,null=True)
    privacy_policy_title = models.CharField(max_length=50,null=True)
    privacy_policy_page= models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    panels = [
        
        MultiFieldPanel(
            [
               FieldPanel("active"),
                FieldPanel("cookie_age"),
            ],"general"),
        MultiFieldPanel(
            [ 
             FieldRowPanel([FieldPanel("privacy_policy_title_fr"),FieldPanel("privacy_policy_title_en"),FieldPanel("privacy_policy_title_ar"),]),
             FieldRowPanel([FieldPanel("privacy_policy_page_fr"),FieldPanel("privacy_policy_page_en"),FieldPanel("privacy_policy_page_ar"),]),
            ],"politique de confidentialité lien"),
        MultiFieldPanel(
                    [
                    FieldRowPanel([FieldPanel("title_fr"),
                    FieldPanel("title_en"),
                    FieldPanel("title_ar"),])
                    ],
                    "Title",
                ),
        MultiFieldPanel(
            [
                FieldPanel("text_fr"),
                FieldPanel("text_en"),
                FieldPanel("text_ar"),
            ],"Text"),
        MultiFieldPanel(
            [
                FieldRowPanel([ FieldPanel("read_button_text_fr"),
                FieldPanel("read_button_text_en"),
                FieldPanel("read_button_text_ar"),])
            ],"Read button text"),
        MultiFieldPanel(
            [
                FieldRowPanel([ FieldPanel("decline_button_text_fr"),
                FieldPanel("decline_button_text_en"),
                FieldPanel("decline_button_text_ar"),])
            ],"Decline button text"),
    ]
    class Meta:
        verbose_name ="Consentement 18-07"



"""***********************************************************************************"""

@register_setting(icon="collapse-up")
class top_navbar(BaseGenericSetting):
    logo = StreamField([("Logo",logoBlock()),],use_json_field=True,blank=True,default=[])
    links = StreamField([
                        ("link",LinkBlock()),
                        ("dropdown",DropdownBlock()),
                       ],use_json_field=True,blank=True,default=[])
    cta_button  = StreamField(
        [("cta", LinkBlock())],
        max_num=1,      
        min_num=1,      
        use_json_field=True,
        blank=False,default=[]
    )
    panels = [
        MultiFieldPanel(
            [
                FieldPanel("logo"),
                FieldPanel("links"),
                FieldPanel("cta_button"),
            ],
            "Top menu",
        )
        ]

"""***********************************************************************************"""
@register_setting(icon="collapse-down")
class preFooter(BaseGenericSetting):
    title_fr = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255,null=True)
    title_ar = models.CharField(max_length=255,null=True)
    buttons = StreamField([("links",LinkBlock()),],use_json_field=True,blank=True,default=[])
    
    panels = [
                MultiFieldPanel(
                    [
                        FieldPanel("title_fr"),
                        FieldPanel("title_en"),
                        FieldPanel("title_ar"),
                        FieldPanel("buttons"),
                    ],
                    "Pre footer",
                )
            ]

"""***********************************************************************************"""
@register_setting(icon="collapse-down")
class footer(BaseGenericSetting):
    logo_fr = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    logo_en=models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    logo_ar=models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    text_fr = RichTextField(null=True)
    text_en = RichTextField(null=True)
    text_ar = RichTextField(null=True)
    links = StreamField([("links",LinksBlock()),],use_json_field=True,blank=True,default=[])
    copyrights_fr = RichTextField(null=True,)
    copyrights_en = RichTextField(null=True,)
    copyrights_ar = RichTextField(null=True,)
    panels = [
            MultiFieldPanel(
                [
                    FieldPanel("logo_fr"),
                    FieldPanel("logo_en"),
                    FieldPanel("logo_ar"),
                    FieldPanel("text_fr"),
                    FieldPanel("text_en"),
                    FieldPanel("text_ar"),
                    FieldPanel("links"),
                    FieldPanel("copyrights_fr"),
                    FieldPanel("copyrights_en"),
                    FieldPanel("copyrights_ar"),
                ],
                "Footer",
            )
        ]


"""***********************************************************************************"""

@register_setting(icon="info-circle-fill")
class contactstInfos(BaseGenericSetting):    
    map_loaction = models.CharField(max_length=500) 
    social_medias = StreamField([
        ('socialmediablock',SocialMediaBlock())
        ])
    adresse = models.CharField(max_length=150)
    numero_telephone = models.CharField(max_length=15)
    email = models.CharField(max_length=50) 
    
    panels = [
                MultiFieldPanel(
                    [
                        FieldPanel("map_loaction"),
                        MultiFieldPanel(
                                    [
                                         FieldRowPanel([
                                        FieldPanel("adresse_fr"),
                                        FieldPanel('adresse_en'),
                                        FieldPanel('adresse_ar'),
                                    ]),],""),
                        FieldPanel("numero_telephone"),
                        FieldPanel("email"),
                        FieldPanel("social_medias"),
                    ],
                    "contactstInfos",
                )
            ]



"""***********************************************************************************"""

from modelcluster.fields import ParentalKey
class AgenceContact(Orderable):
    page = ParentalKey('Agence', on_delete=models.CASCADE, related_name='contacts')
    contact_type = models.CharField(max_length=50, choices=[
        ('email', 'Email'),
        ('fax', 'FAX'),
        ('fix', 'FIX'),
        ('mobile', 'Mobile'),
    ])
    value = models.CharField(max_length=255)

    panels = [
        FieldPanel('contact_type'),
        FieldPanel('value'),
    ]   
@register_snippet
class Wilaya(ClusterableModel):
    active=models.BooleanField(null=True,default=True)
    nom = models.CharField(max_length=255,null=True)
    code = models.CharField(max_length=5,unique=True)
    
    panels = [
        FieldPanel('active'),
         MultiFieldPanel(
                    [
                        FieldPanel('nom_fr'),
                        FieldPanel('nom_en'),
                        FieldPanel('nom_ar'),
                    ],"Nom"),
        FieldPanel('code'),
    ]

    def __str__(self):
        return self.nom
    class Meta:
        verbose_name="Wilaya"
        verbose_name_plural="Wilayas"

@register_snippet
class Commune(ClusterableModel,TranslatableMixin):
    active = models.BooleanField(null=True)
    code =  models.CharField(max_length=255)
    nom = models.CharField(max_length=255)
    wilaya  = models.ForeignKey('Wilaya', on_delete=models.CASCADE)
    panels = [
        FieldPanel('active'),
        FieldPanel('nom'),
        FieldPanel('code'),
        FieldPanel('wilaya'),    
    ]
    translatable_fields = [
        SynchronizedField("code"),
        TranslatableField("nom"),
    ]
    def __str__(self):
        return self.nom
    class Meta(TranslatableMixin.Meta):
        verbose_name="Commune"
        verbose_name_plural="Communes"


@register_snippet
class Agence(ClusterableModel):
    active = models.BooleanField(null=True,default=True)
    code =  models.CharField(max_length=255)
    nom = models.CharField(max_length=255)
    responsable = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)
    wilaya  = models.ForeignKey('Wilaya', on_delete=models.CASCADE,null=True)
    localisation = models.CharField(max_length=500)
    panels = [
        FieldPanel('active'),
        FieldPanel('code'),
        MultiFieldPanel(
            [
                 FieldRowPanel([
                FieldPanel('nom_fr'),
                FieldPanel('nom_en'),
                FieldPanel('nom_ar'),
            ]),],"Nom"),
        MultiFieldPanel(
            [ FieldRowPanel([
                FieldPanel('adresse_fr'),
                FieldPanel('adresse_en'),
                FieldPanel('adresse_ar'),
            ]),],"adresse"), 
        MultiFieldPanel(
            [
            FieldRowPanel([
                FieldPanel('responsable_fr'),
                FieldPanel('responsable_en'),
                FieldPanel('responsable_ar'),
            ]),],"responsable"),

        InlinePanel('contacts', label="Agency Contacts"),
        FieldPanel('wilaya'),
        FieldPanel('localisation'),
    ]
    def __str__(self):
        return self.nom +" ["+self.code+"]"
    class Meta:
        verbose_name="Agence"
        verbose_name_plural="Agences"
        
        
        


class MentionsLegalesPage(Page):
    subtitle = models.CharField(max_length=200)
    text = StreamField([
        ("text_blocks",ParagraphBlock()),
    ])
    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("text"),
    ]


class DocumentsLegalesPage(Page):
    subtitle = models.CharField(max_length=200)
    sections = StreamField(
        [
            ("Document_section", DocumentBlock()),
        ],
        use_json_field=True,
        blank=True,
        default=[],
    )
    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("sections"),
    ]


