from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
 
class oneProductBlock(blocks.StructBlock):
    products = blocks.ListBlock(
            blocks.StructBlock([
                    ("title",blocks.CharBlock()),
                    ("text",blocks.RichTextBlock()),
                    ("image",ImageChooserBlock()),
                    ("button_text",blocks.CharBlock()),
                    ("linked_page",blocks.PageChooserBlock()),
                ])
    )
    class Meta:
        template = "products/blocks/one_product_block.html"
        icon = "0-square-fill"
       

class multipleProducstBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    subtitle = blocks.CharBlock()
    products = blocks.ListBlock(
                blocks.StructBlock([
                    ("title",blocks.CharBlock()),
                    ("text",blocks.RichTextBlock()),
                    ("image",ImageChooserBlock()),
                    ("button_text",blocks.CharBlock()),
                    ("linked_page",blocks.PageChooserBlock()),
                ])
    )
    class Meta:
        template = "products/blocks/multiple_products_block.html"
        icon = "0-square-fill"
       

