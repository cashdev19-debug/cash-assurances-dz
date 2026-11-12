from wagtail import blocks

class FaqBlock(blocks.StructBlock):
    active = blocks.BooleanBlock(default=True)
    question=blocks.CharBlock(max_length=200)
    response=blocks.TextBlock()


class CategoryFaqsBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    faqs=blocks.ListBlock(FaqBlock())
    class Meta:
        icon = "doc-full-inverse"
        form_classname = "logo-block struct-block"

