
from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField

from .blocks import *
from wagtail.admin.panels import (
    FieldPanel, )
from wagtail.fields import StreamField
from django.utils.functional import cached_property
from collections import defaultdict

class OrganigrammePage(Page):
    subtitle =models.CharField(max_length=100)
    organigramme =   StreamField(
        [   ("niveau_0", niveau_0()),
           ("niveau_1", niveau_1()),
           ("niveau_2", niveau_2()),  
        ],
        use_json_field=True,
        blank=True,
        default=[],
    )
    content_panels = Page.content_panels + [
            FieldPanel("subtitle"),
            FieldPanel("organigramme"),
        ]
    
    @cached_property
    def grouped_blocks(self):
        groups = defaultdict(list)
        
        for block in self.organigramme:
            groups[block.block_type].append(block)
            
        return groups
    