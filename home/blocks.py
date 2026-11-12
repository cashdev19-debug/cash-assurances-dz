
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtailiconchooser.blocks import IconChooserBlock
from wagtail.contrib.forms.models import AbstractEmailForm
from wagtailvideos.blocks import VideoChooserBlock
class CarouselBlock(blocks.StructBlock):
    slide = blocks.ListBlock(
          blocks.StructBlock([
        ("title",blocks.CharBlock()),
        ("subtitle",blocks.CharBlock()),
        ("video",VideoChooserBlock()),
        ("button_text",blocks.CharBlock()),
        ("linked_page",blocks.PageChooserBlock(required = False)),
    ])
    )
    class Meta:
        template = "home/blocks/carousel_card.html"
        icon = "doc-full-inverse"
        form_classname = "produit-block struct-block"
        form_attrs = {
            # This block has additional customizations enabled
            "data-controller": "magic1",
            "data-action": "click->magic#abracadabra1",
        }


class DevisBlock(blocks.StructBlock):
    devis = blocks.ListBlock(
        blocks.StructBlock([
            ("title",blocks.CharBlock()),
            ("text",blocks.CharBlock()),
            ("icon",IconChooserBlock()),
            ("linked_page",blocks.PageChooserBlock()),
    ])
    )
    class Meta:
        template = "home/blocks/devis_card.html"
        icon = "doc-full-inverse"
        form_classname = "produit-block struct-block"
        form_attrs = {
            # This block has additional customizations enabled
            "data-controller": "magic1",
            "data-action": "click->magic#abracadabra1",
        }


 
class ProduitBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    subtitle = blocks.CharBlock()
    produit = blocks.ListBlock(
        blocks.StructBlock([
            ("title",blocks.CharBlock()),
            ("text",blocks.CharBlock()),
            ("image",ImageChooserBlock()),
            ("icon",IconChooserBlock()),
            ("button_text",blocks.CharBlock()),
            ("linked_page",blocks.PageChooserBlock()),
        ])
    )
    class Meta:
        template = "home/blocks/produit_card.html"
        icon = "doc-full-inverse"
        form_classname = "produit-block struct-block"
        form_attrs = {
            # This block has additional customizations enabled
            "data-controller": "magic1",
            "data-action": "click->magic#abracadabra1",
        }
 
class TemoignageBlock(blocks.StructBlock):
    title =blocks.CharBlock()
    subtitle=blocks.CharBlock()
    temoignage=blocks.ListBlock(
          blocks.StructBlock([
            ("nom",blocks.CharBlock()),
            ("image",ImageChooserBlock()),
            ("rating",blocks.IntegerBlock(min_value=0,max_value=5)),
            ("text",blocks.RichTextBlock()),
            ("agence",blocks.CharBlock()),
            ("date",blocks.DateBlock()),
            ("link",blocks.URLBlock()),
        ])
    )
    class Meta:
        template = "home/blocks/temoignage_block.html"
        icon = "doc-full-inverse"
        form_classname = "temoignage-block struct-block"
        form_attrs = {
            # This block has additional customizations enabled
            "data-controller": "magic1",
            "data-action": "click->magic#abracadabra1",
        }


class RecrutementBlock(blocks.StructBlock):
    title =blocks.CharBlock()
    text=blocks.RichTextBlock()
    icon = IconChooserBlock()
    link_text = blocks.CharBlock()
    link = blocks.PageChooserBlock()

    class Meta:
        template = "home/blocks/recrutement_block.html"
        icon = "form"
        form_classname = "recrutement-block struct-block"


class contactBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    subtitle = blocks.CharBlock(max_length=150)
    form = blocks.PageChooserBlock(page_type="home.FormPage")
    class Meta : 
        template = "home/blocks/contact_block.html"


class FormChooserBlock(blocks.PageChooserBlock):
    title = blocks.CharBlock(max_length=100)
    subtitle = blocks.CharBlock(max_length=150)
    form = blocks.PageChooserBlock(page_type="home.FormPage")
    class Meta:
        template = "home/blocks/contact_block.html"


class newsletterBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    subtitle = blocks.CharBlock(max_length=150)
    background_img= ImageChooserBlock()
    form = blocks.PageChooserBlock(page_type="home.FormPage")

    class Meta : 
        template = "home/blocks/newsletter_block.html"


class button_block(blocks.StructBlock):
    button_text = blocks.CharBlock(max_length=50)
    button_icon = IconChooserBlock()
    button_url = blocks.PageChooserBlock()


class question_block(blocks.StructBlock):
    question = blocks.CharBlock(max_length=255)
    response = blocks.TextBlock()
    
class mobile_block(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    subtitle = blocks.CharBlock(max_length=150)
    cover_image= ImageChooserBlock()
    button = blocks.ListBlock(button_block)
    class Meta : 
        template = "home/blocks/mobile_block.html"



class faq_block(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    subtitle = blocks.CharBlock(max_length=150)
    cover_image= ImageChooserBlock()
    question = blocks.ListBlock(question_block)
    class Meta : 
        template = "home/blocks/faq_block.html"


class annualReport_block(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    subtitle = blocks.CharBlock(max_length=150)
    cover_image= ImageChooserBlock()
    button = blocks.ListBlock(button_block)
    class Meta : 
        template = "home/blocks/annualReport_block.html"
