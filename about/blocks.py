from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtailiconchooser.blocks import IconChooserBlock
from wagtail.contrib.forms.models import AbstractEmailForm

class PresentationBlock(blocks.StructBlock):
    title=blocks.RichTextBlock()
    text=blocks.RichTextBlock()
    images=blocks.ListBlock(ImageChooserBlock())
    numbers = blocks.ListBlock(blocks.StructBlock([
        ("title",blocks.CharBlock()),
        ("subtitle",blocks.CharBlock()), 
    ]))
    class Meta:
        template = "about/blocks/presentation_block.html"
        icon = "easel2"


class TimelineBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    subtitle =blocks.CharBlock()
    timeline= blocks.ListBlock(blocks.StructBlock([
        ("title",blocks.CharBlock()),
        ("text",blocks.RichTextBlock()),
        ("image",ImageChooserBlock()),
    ]))
    
    class Meta:
        template = "about/blocks/timeline_block.html"
        icon = "clock-history"



class PointsRepereBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    subtitle =blocks.CharBlock()
    points = blocks.ListBlock(blocks.StructBlock([
        ("title",blocks.CharBlock()),
        ("body",blocks.RichTextBlock()),
        ("icon",IconChooserBlock()),
    ]))
    
    class Meta:
        template = "about/blocks/points_repere_block.html"
        icon = "list-stars"


class CounterBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False,blank=True)
    subtitle =blocks.CharBlock(required=False,blank=True)
    chiffre = blocks.ListBlock(blocks.StructBlock([
        ("icon",IconChooserBlock()),
        ("title",blocks.CharBlock()),
        ("valeur",blocks.FloatBlock()),
        ("unite",blocks.CharBlock()),
    ]))
    
    class Meta:
        template = "about/blocks/counter_block.html"
        icon = "sort-numeric-up-alt"

class StatsCardBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False,blank=True)
    subtitle =blocks.CharBlock(required=False,blank=True)
    chiffre = blocks.ListBlock(blocks.StructBlock([
        ("icon",IconChooserBlock()),
        ("title",blocks.CharBlock()),
        ("subtitle",blocks.CharBlock()),
    ]))
    
    class Meta:
        template = "about/blocks/stats_card_block.html"
        icon = "sort-numeric-up-alt"



class HumainCapitalBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False,blank=True)
    subtitle =blocks.CharBlock(required=False,blank=True)
    image = ImageChooserBlock() 
    
    class Meta:
        template = "about/blocks/humain_capital_block.html"
        icon = "person-check"


