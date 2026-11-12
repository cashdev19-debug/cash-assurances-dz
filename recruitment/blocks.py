from wagtail import blocks


class contactBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    subtitle = blocks.CharBlock(max_length=150)
    form = blocks.PageChooserBlock(page_type="home.FormPage")
    class Meta : 
        template = "home/blocks/contact_block.html"

