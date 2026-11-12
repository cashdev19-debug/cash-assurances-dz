from wagtail import blocks
from wagtail_color_panel.blocks import NativeColorBlock
from wagtailiconchooser.blocks import IconChooserBlock



class niveau_0(blocks.StructBlock):
    title = blocks.CharBlock()
    subtitle = blocks.CharBlock()
    class Meta:
        icon = "0-square"
        form_classname = "produit-block struct-block"


class niveau_1(blocks.StructBlock):
    title = blocks.CharBlock()
    subtitle =blocks.CharBlock()
    background_color = NativeColorBlock(default="#ffffff")
    class Meta:
        icon = "1-square"
        form_classname = "produit-block struct-block"



class niveau_2(blocks.StructBlock):
    icon = IconChooserBlock()
    title = blocks.CharBlock()
    subtitle =blocks.CharBlock()
    background_color = NativeColorBlock(default="#ffffff")
    
    subDirection = blocks.ListBlock(
        blocks.StructBlock([
            ("title",blocks.CharBlock()),
            ("subtitle",blocks.CharBlock()),
    ])
    )
    class Meta:
        icon = "2-square"
        form_classname = "produit-block struct-block"

