
from wagtail import blocks
from wagtail.blocks import RichTextBlock
from wagtail.images.blocks import ImageChooserBlock

from wagtail.documents.blocks import DocumentChooserBlock
from wagtailiconchooser.blocks import IconChooserBlock
from django.utils.translation import get_language
class logoBlock(blocks.StructBlock):
    logo = blocks.StructBlock([
            ("logo_fr",ImageChooserBlock()),
            ("logo_en",ImageChooserBlock()),
            ("logo_ar",ImageChooserBlock()),
        ])

    class Meta:
        template = "base/blocks/logo_block.html"
        icon = "doc-full-inverse"
        form_classname = "logo-block struct-block"

from wagtail.blocks import StructValue
LANGS = ("fr", "en", "ar")
class CTAStructValue(StructValue):
    def _lang_order(self):
        lang = (get_language() or "fr")[:2]
        return [lang] + [code for code in LANGS if code != lang]

    def _localized(self, prefix):
        """Return the first non-empty `<prefix>_<lang>` value, current language first."""
        for code in self._lang_order():
            value = self.get(f"{prefix}_{code}")
            if value:
                return value
        return None

    @property
    def title(self):
        return self._localized("title") or ""

    @property
    def href(self):
        # 1. Page (current language first, then fallback)
        for code in self._lang_order():
            page = self.get(f"link_page_{code}")
            if page and page.url:
                return page.url

        # 2. Document
        document = self.get("link_document")
        if document:
            return document.url

        # 3. External URL
        return self.get("link_url") or ""


class LinkBlock(blocks.StructBlock):


    title_fr = blocks.CharBlock(required=True)
    title_en = blocks.CharBlock(required=True,null=True)
    title_ar = blocks.CharBlock(required=True,null=True)
    link_page_fr = blocks.PageChooserBlock(required=False)
    link_page_en = blocks.PageChooserBlock(required=False,null=True)
    link_page_ar = blocks.PageChooserBlock(required=False,null=True)
    link_document = DocumentChooserBlock(required=False,help_text="Used if no page  is selected")
    link_url = blocks.URLBlock(required=False, help_text="Used if no page or document is selected")
    
    class Meta:
        template = "base/blocks/link_block.html"
        icon = "link"
        value_class = CTAStructValue



class LinksBlock(blocks.StructBlock):
    title_fr = blocks.CharBlock(required=True , max_length=255)
    title_en = blocks.CharBlock(required=True , max_length=255,null=True)
    title_ar = blocks.CharBlock(required=True , max_length=255,null=True)
    links = blocks.StreamBlock([('link', LinkBlock()),
                                ])
    
    class Meta:
        icon = "list-ul"


class DropdownBlock(blocks.StructBlock):
    title_fr = blocks.CharBlock(required=True)
    title_en = blocks.CharBlock(required=True,null=True)
    title_ar= blocks.CharBlock(required=True,null=True)
    # This allows multiple MenuItemBlocks inside the dropdown
    menu_items = blocks.StreamBlock([
        ('link', LinkBlock()),
        ('sub_dropdown', blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('items', blocks.ListBlock(LinkBlock())) # Second level
        ])),
    ])

    class Meta:
        template = "base/blocks/dropdown_block.html"
        icon = "arrow-down"



class DocumentBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    documents = blocks.ListBlock(
                blocks.StructBlock([
                    ("title",blocks.CharBlock()),
                    ("document",DocumentChooserBlock()),
                ]))
    class Meta:
        icon = "filetype-pdf"


class ParagraphBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    text = RichTextBlock()
    class Meta:
        icon = "doc-full"



class SocialMediaBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    link = blocks.URLBlock()
    icon = IconChooserBlock()   
    class Meta:
        icon = "globe"






