
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.models import Page
from wagtailiconchooser.blocks import IconChooserBlock
from wagtail.contrib.forms.models import AbstractEmailForm





class DocumentsBlock(blocks.StructBlock):
    title=blocks.CharBlock(max_length=100)
    subtitle=blocks.CharBlock(max_length=120)
    date=blocks.DateBlock()
    cover_image=ImageChooserBlock()
    document_pdf=DocumentChooserBlock()
    class Meta:
        template = "press_reports/blocks/documents_block.html"
        icon = "doc-full-inverse"
        form_classname = "logo-block struct-block"

