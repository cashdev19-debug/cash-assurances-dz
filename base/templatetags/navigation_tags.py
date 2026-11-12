from django import template

# import site:
from wagtail.models import Site, Locale
from django.utils.html import format_html,format_html_join
from products.models import Product,ProductCategory
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.simple_tag(takes_context=True)
def get_site_root(context):
    return Site.find_for_request(context["request"]).root_page


@register.simple_tag
def print_multiple(value, count):
    return " ".join([value] * int(count))




@register.simple_tag
def purecounterDisplay(value):
    if not value.is_integer():
        return format_html(
            "<span data-purecounter-start='0' data-purecounter-end='{}' data-purecounter-duration='1' data-purecounter-decimals='1' data-purecounter-separator='.' class='purecounter'><p></p></span>",
            value,
        )
    else:
        return format_html(
            "<span data-purecounter-start='0' data-purecounter-end='{}' data-purecounter-duration='1'  class='purecounter'><p></p></span>",
            value,
        )


@register.inclusion_tag('products/tags/products.html', takes_context=True)
def products(context):
    return {
        'products': Product.objects.filter(locale=Locale.get_active()),
        'request': context['request'],
    }


@register.inclusion_tag('products/tags/product_categories.html', takes_context=True)
def productCategories(context):
    return {
        'categories': ProductCategory.objects.filter(locale=Locale.get_active()),
        'request': context['request'],
    }


@register.simple_tag
def div_class_block(element):
    return element[0]



@register.filter
def is_instance(obj, class_name):
    return obj.__class__.__name__ == class_name



@register.filter
def phoneNumberFormat(contact):
    result = contact.replace(" ","")
    if len(result) == 10:
         result = result[0:2]+ ' '+result[2:4] + ' '+ result[4:6]+' '+ result[6:8]+' '+ result[8:10]
    elif len(result) == 9:
        if result.startswith("0"):
            result = result[0:3]+ ' '+result[3:5] + ' '+ result[5:7]+' '+ result[7:9]
        else : 
            result =  "0"+result
            result = result[0:2]+ ' '+result[2:4] + ' '+ result[4:6]+' '+ result[6:8]+' '+ result[8:10]
    elif len(result) == 8 : 
            result =  "0"+result
            result = result[0:3]+ ' '+result[3:5] + ' '+ result[5:7]+' '+ result[7:9]
    return result
    

@register.simple_tag
def found_results(text, pages, docs):
    if not text:
        return ""
    result = text.replace("{pages}", f'<span class="font-bold text-slate-800 dark:text-slate-200">{pages}</span>')
    result = result.replace("{documents}", f'<span class="font-bold text-slate-800 dark:text-slate-200">{docs}</span>')
    return mark_safe(result)
    

@register.filter
def split_pages(value):
    if not value:
        return ["", "", ""]
    return value.split('{pages}')
    
from django.utils.safestring import mark_safe

from wagtailiconchooser.utils import get_svg_icons
from xml.dom import minidom


@register.simple_tag
def svg_icon(name=None, classname=None, fill=None):
    """
    Load svg icon.

    Usage:
        {% load wagtailiconchooser_tags %}
        ...
        {% svg_icon name="cogs" classname="your-custom-class" %}

    :param name: the icon name/id, required (string)
    :param classname: css classname to add to svg (string)
    """
    if not name:
        return None

    svg_icons = get_svg_icons()

    if svg_icons.get(name):
        svg_str = svg_icons.get(name)
        if classname or fill:
            doc = minidom.parseString(svg_str)
            svg = doc.getElementsByTagName("svg")[0]
            svg.setAttribute("fill", "currentColor")
            svg.setAttribute("class", classname)
            return mark_safe(svg.toxml())
        else:
            return svg_str
    return format_html('<svg aria-hidden="true" viewBox="0 0 24 24" class="{}"><use xlink:href="#icon-{}"> </svg>',classname, name)



def _clean_text(html_fragment: str) -> str:
    """Strip remaining inline tags and decode basic entities."""
    text = re.sub(r"<[^>]+>", "", html_fragment)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    return text.strip()


@register.filter
def richtext_lists(value):
    """
    Parse rich text HTML and return a list of "segments".
    Each segment is either:
        {"type": "list", "ordered": bool, "items": [str, ...]}
        {"type": "html", "content": "<p>...</p>"}
    This lets the template render lists with Tailwind and keep other HTML intact.
    """
    if not value:
        return []

    html = str(value)
    segments = []

    # Match <ul>...</ul> or <ol>...</ol> blocks (non-greedy, multiline)
    list_pattern = re.compile(
        r"<(ul|ol)\b[^>]*>(.*?)</\1>", re.DOTALL | re.IGNORECASE
    )

    pos = 0
    for match in list_pattern.finditer(html):
        # Everything before the list is raw HTML
        before = html[pos:match.start()].strip()
        if before:
            segments.append({"type": "html", "content": before})

        tag = match.group(1).lower()
        inner = match.group(2)

        # Extract each <li>...</li> inside the list (handles nesting too)
        items = [
            _clean_text(li)
            for li in re.findall(r"<li\b[^>]*>(.*?)</li>", inner, re.DOTALL | re.IGNORECASE)
        ]
        items = [i for i in items if i]

        segments.append(
            {"type": "list", "ordered": tag == "ol", "items": items}
        )
        pos = match.end()

    # Remaining HTML after the last list
    after = html[pos:].strip()
    if after:
        segments.append({"type": "html", "content": after})

    return segments


@register.filter
def plain_list(value):
    """Return just the items of the FIRST list found, or empty list."""
    for seg in richtext_lists(value):
        if seg["type"] == "list":
            return seg["items"]
    return []


@register.filter
def style_quotes(value):
    """
    Finds text inside quotes or text containing 'quot' and wraps it in a styled blockquote.
    """
    if not value:
        return ""

    # Converts RichText object to HTML string
    content = str(value)
    # Example 1: Converts existing standard <blockquote> tags into styled ones
    
    pattern = r'<blockquote([^>]*)>(.*?)</blockquote>'

    def replacer(match):
        attrs = match.group(1)   # e.g., ' data-block-key="1a2b3"'
        inner_text = match.group(2) # Quote body content
        return f'<blockquote class="relative ps-4 sm:ps-6 border-s-2 border-e-2 my-10 border-cash/60 bg-black/10 p-5 rounded-2xl"><div class="relative "><p class="text-black/60 sm:text-xl"><em>{inner_text}</em></p></div></blockquote>'
    transformed = re.sub(pattern, replacer, content, flags=re.DOTALL | re.IGNORECASE)
    return mark_safe(transformed)

    return mark_safe(content)