from .models import SearchPageText
from modeltranslation.translator import TranslationOptions,register

@register(SearchPageText)
class SiteSettingTranslationOptions(TranslationOptions):
    fields = (
        'subtitle',
        'modal_search_placeholder',
        'modal_first_heading_text',
        'modal_no_results_text',
        'modal_view_all_text',
        'search_placeholder',
        'search_button_text',
        'result_heading_text',
        'first_heading_text',
        'no_results_text',
        'found_heading',
        'pages_title',
        'documents_title',
    )
