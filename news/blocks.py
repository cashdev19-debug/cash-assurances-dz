from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.blocks import RichTextBlock
class CategoryBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    clear_filter_text = blocks.CharBlock()
    clear_filter_button_text = blocks.CharBlock()
    class Meta:
        template = "news/blocks/category_block.html"
        icon = "doc-full-inverse"
        form_classname = "logo-block struct-block"


class NewsLetterBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    subtitle = blocks.CharBlock(max_length=150)
    form = blocks.PageChooserBlock(page_type="home.FormPage")

    class Meta:
        template = "news/blocks/news_letter_block.html"
        icon = "doc-full-inverse"
        form_classname = "logo-block struct-block"


class PaginationStructBlock(blocks.StructBlock):
    next_page = blocks.CharBlock(required=False, default="Suivant")
    previous_page = blocks.CharBlock(required=False, default="Précédent")
    showing_pages_text = blocks.CharBlock(required=False, default="Affiche pages")

    class Meta:
        icon = "arrows-expand-vertical"
        label = "Pagination options"