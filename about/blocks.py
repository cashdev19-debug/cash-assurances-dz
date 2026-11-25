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



class TitleImageBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False,blank=True)
    subtitle =blocks.CharBlock(required=False,blank=True)
    image = ImageChooserBlock() 
    
    class Meta:
        template = "about/blocks/title_image_block.html"
        icon = "image"


import math
import re

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import get_language_bidi
from wagtail import blocks

from .capital_humain_layout import (
    CANVAS_H, CANVAS_W, CENTER, CENTRE_TEXT_WIDTH, RING_IN, RING_OUT, SLOTS,
)


def _f(v):
    return f"{v:.1f}"


def _pct(v, total):
    return f"{v / total * 100:.3f}%"


def _titre_html(text):
    t = conditional_escape(text or "")
    t = re.sub(r"\*\*(.+?)\*\*", r'<b class="font-semibold">\1</b>', t)
    return mark_safe(t.replace("|", "<br>"))


class BulleValeurBlock(blocks.StructBlock):
    prefix = blocks.CharBlock(label="Préfixe", required=False, max_length=5, help_text="Ex. : +")
    valeur = blocks.DecimalBlock(label="Valeur")
    decimals = blocks.IntegerBlock(
        label="Décimales (nombres apres la virgule)", required=False, min_value=0, max_value=3,
        help_text="Laisser vide pour une détection automatique.",
    )
    unite = blocks.CharBlock(label="Unité", required=False, max_length=10, help_text="Ex. : %, MDA")
    unite_dessous = blocks.BooleanBlock(label="Unité sous le chiffre", required=False)
    symbole = blocks.CharBlock(label="Symbole", required=False, max_length=3, help_text="Ex. : ♀ ou ♂")


class BulleBlock(blocks.StructBlock):
    valeurs = blocks.ListBlock(
        BulleValeurBlock(), label="Chiffre(s) dans la bulle", min_num=1, max_num=2,
        help_text="Un seul chiffre en général ; deux pour une répartition (ex. 39 % ♀ / 61 % ♂).",
    )
    label = blocks.CharBlock(label="Légende", max_length=80)
    sous_label = blocks.CharBlock(label="Sous-légende", required=False, max_length=60)


class CapitalHumainBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Sur-titre", required=False)
    subtitle = blocks.CharBlock(label="Titre", required=False)
    centre = blocks.CharBlock(
        label="Texte du centre", default="Nos **talents**|font notre|**force**", max_length=80,
        help_text="**mot** = gras. Le texte passe à la ligne tout seul ; | force un retour à la ligne (facultatif).",
    )
    bulles = blocks.ListBlock(
        BulleBlock(), label="Bulles", min_num=1, max_num=6,
        help_text="Ordre = sens horaire, en partant de la bulle en haut à gauche.",
    )

    class Meta:
        template = "about/blocks/capital_humain_block.html"
        icon = "group"
        label = "Capital humain (bulles animées)"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        
        mx = (lambda x: CANVAS_W - x) if get_language_bidi() else (lambda x: x)
        cx, cy = mx(CENTER[0]), CENTER[1]
        bubbles = []

        for i, item in enumerate(list(value["bulles"])[: len(SLOTS)]):
            s = dict(SLOTS[i])
            s["x"], s["lx"] = mx(s["x"]), mx(s["lx"])
            s["dot"] = (mx(s["dot"][0]), s["dot"][1])
            dx, dy = s["x"] - cx, s["y"] - cy
            d = math.hypot(dx, dy)
            ux, uy = dx / d, dy / d
            gx, gy = s["dot"][0] - cx, s["dot"][1] - cy
            gd = math.hypot(gx, gy)
            t = 0.6 + i * 0.15

            vals = []
            for v in item["valeurs"]:
                val = v["valeur"]
                dec = v["decimals"] if v["decimals"] is not None else _decimals1(val)
                vals.append({
                    "prefix": v["prefix"] or "",
                    "unite": v["unite"] or "",
                    "below": v["unite_dessous"],
                    "symbole": v["symbole"] or "",
                    "target": repr(float(val)),   
                    "decimals": dec,
                    "final": number_format(val, decimal_pos=dec, use_l10n=True, force_grouping=True),
                })

            bubbles.append({
                "valeurs": vals,
                "xl": len(vals) == 1 and not vals[0]["unite"] and not vals[0]["symbole"],
                "label": item["label"],
                "sous_label": item["sous_label"],
                "left": _pct(s["x"] - s["r"], CANVAS_W),
                "top": _pct(s["y"] - s["r"], CANVAS_H),
                "width": _pct(s["r"] * 2, CANVAS_W),
                "lx": _pct(s["lx"], CANVAS_W),
                "ly": _pct(s["ly"], CANVAS_H),
                "red": {
                    "x1": _f(cx + ux * RING_IN), "y1": _f(cy + uy * RING_IN),
                    "x2": _f(cx + ux * (d - s["r"])), "y2": _f(cy + uy * (d - s["r"])),
                },
                "grey": {
                    "x1": _f(cx + gx / gd * RING_OUT), "y1": _f(cy + gy / gd * RING_OUT),
                    "x2": s["dot"][0], "y2": s["dot"][1],
                },
                "dot": s["dot"],
                "t": f"{t:.2f}",
                "t_pop": f"{t + 0.2:.2f}",
                "t_dot": f"{t + 0.9:.2f}",
                "t_label": f"{t + 1.0:.2f}",
                "t_float": f"{i * 0.4 + 1.5:.1f}",
                "t_card": f"{0.3 + i * 0.12:.2f}",
                "t_card_label": f"{0.5 + i * 0.12:.2f}",
            })

        context["bubbles"] = bubbles
        context.update({
            "canvas_w": CANVAS_W, "canvas_h": CANVAS_H,
            "cx": cx, "cy": cy, "ring_in": RING_IN, "ring_out": RING_OUT,
            "centre": {
                "left": _pct(cx - RING_IN, CANVAS_W),
                "top": _pct(cy - RING_IN, CANVAS_H),
                "width": _pct(RING_IN * 2, CANVAS_W),
                "text_w": f"{CENTRE_TEXT_WIDTH * 100:.0f}%",
            },
        })
        context["centre_html"] = _titre_html(value["centre"])
        return context

