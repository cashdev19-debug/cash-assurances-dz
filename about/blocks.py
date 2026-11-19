from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtailiconchooser.blocks import IconChooserBlock
from wagtail.contrib.forms.models import AbstractEmailForm
from django.utils.formats import number_format
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
        ("subtitle",blocks.CharBlock()),
        ("body",blocks.RichTextBlock()),
        ("icon",IconChooserBlock()),
    ]))
    
    class Meta:
        template = "about/blocks/points_repere_block.html"
        icon = "list-stars"


from uuid import uuid4 
 
 
def _decimals(values):
    """Max number of decimals needed to display the series (22.3 -> 1, 21.0 -> 0)."""
    d = 0
    for v in values:
        s = f"{v:.3f}".rstrip("0").rstrip(".")
        if "." in s:
            d = max(d, len(s.split(".")[1]))
    return d
 
 
 
 
 
def _decimals1(value):
    """Decimals needed to display a number (21.0 -> 0, 24.3 -> 1)."""
    s = f"{value:.3f}".rstrip("0").rstrip(".")
    return len(s.split(".")[1]) if "." in s else 0
 
class AnneeValeurBlock(blocks.StructBlock):
    annee = blocks.CharBlock(label="Année", max_length=10)
    value = blocks.FloatBlock(label="Valeur")
 
    class Meta:
        icon = "date"
        label = "Année"
 
 
class UnChiffreBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        label="Titre",
        help_text="Ex. : « Capital social » ou « Ratio de solvabilité 1 ».",
    )
    subtitle = blocks.CharBlock(
        label="Sous-titre / légende", required=False,
        help_text="Ex. : « (+5 % en 2025 | CAGR : +20 %/an) » ou « (rapportée au chiffre d’affaires) ».",
    )
    unit = blocks.CharBlock(
        label="Unité", required=False, max_length=30,
        help_text="Ex. : « milliards DA ». Mettre « % » pour afficher les valeurs en pourcentage.",
    )
    show_total = blocks.BooleanBlock(
        label="Afficher la dernière valeur en grand titre", required=False, default=True,
        help_text="Décoché : le titre devient l’en-tête (cas des ratios).",
    )
    decimals = blocks.IntegerBlock(
        label="Décimales (optionnel)", required=False, min_value=0, max_value=3,
        help_text="Laisser vide pour les déduire automatiquement des valeurs.",
    )
    annee = blocks.ListBlock(AnneeValeurBlock(), label="Années", min_num=2)
 
    class Meta:
        icon = "sort-numeric-up-alt"
        label = "Chiffre clé"
 
 
class ChiffresClesBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre de la section", required=False)
    subtitle = blocks.CharBlock(label="Sous-titre de la section", required=False)
    chiffre = blocks.ListBlock(UnChiffreBlock(), label="Chiffres clés")
 
    class Meta:
        template = "about/blocks/chiffres_cles_block.html"
        icon = "sort-numeric-up-alt"
        label = "Chiffres clés"
 
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        cards = []
        for c in value["chiffre"]:
            labels = [a["annee"] for a in c["annee"]]
            values = [a["value"] for a in c["annee"]]
            unit = (c["unit"] or "").strip()
            decimals = c["decimals"] if c["decimals"] is not None else _decimals(values)
            card = {"labels": labels, "values": values, "decimals": decimals}
            if unit == "%":
                card["unit"] = "%"
            if c["show_total"]:
                card.update(
                    headline="{n} " + unit if unit else "{n}",
                    countTo=values[-1],
                    countDecimals=decimals,
                    subtitle=c["title"],
                    caption=c["subtitle"],
                )
            else:
                card.update(headline=c["title"], subtitle=c["subtitle"])
            cards.append(card)
 
        uid = uuid4().hex[:8]
        context["uid"] = uid
        context["data_id"] = f"kf-data-{uid}"
        context["kf_config"] = {"cards": cards}
        return context



class CompteurItemBlock(blocks.StructBlock):
    # Existing field names are kept so saved content keeps loading.
    icon = IconChooserBlock(label="Icône")
    title = blocks.CharBlock(label="Titre", max_length=80)
    valeur = blocks.FloatBlock(label="Valeur")
    unite = blocks.CharBlock(
        label="Unité", required=False, max_length=30,
        help_text="Ex. : %, ans, M DA. Laisser vide si inutile.",
    )
    # New optional fields
    prefix = blocks.CharBlock(
        label="Préfixe", required=False, max_length=5, help_text="Ex. : + ou ~",
    )
    description = blocks.CharBlock(
        label="Description", required=False, max_length=120,
        help_text="Petite ligne sous le chiffre.",
    )
    decimals = blocks.IntegerBlock(
        label="Décimales (optionnel)", required=False, min_value=0, max_value=3,
        help_text="Laisser vide pour les déduire de la valeur.",
    )
 
    class Meta:
        icon = "sort-numeric-up-alt"
        label = "Compteur"
 
 
class CounterBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Sur-titre", required=False)
    subtitle = blocks.CharBlock(label="Titre", required=False)
    chiffre = blocks.ListBlock(CompteurItemBlock(), label="Compteurs", min_num=1)
 
    class Meta:
        template = "about/blocks/counter_block.html"
        icon = "sort-numeric-up-alt"
        label = "Compteurs animés"
 
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        cards = []
        for c in value["chiffre"]:
            v = c["valeur"]
            d = c["decimals"] if c["decimals"] is not None else _decimals1(v)
            cards.append({
                "icon": c["icon"],
                "title": c["title"],
                "description": c["description"],
                "prefix": c["prefix"],
                "unit": c["unite"],
                # str so Django doesn't localise "24.3" into "24,3" inside a data attribute
                "target": repr(float(v)),
                "decimals": d,
                # Localised final value: shown without JS, to screen readers, and at the end of the count
                "final": number_format(v, decimal_pos=d, use_l10n=True, force_grouping=True),
            })
        context["cards"] = cards
        return context
    
    
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


