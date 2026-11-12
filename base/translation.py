from .models import loi_18_07_consentement,Wilaya,Agence,contactstInfos
from modeltranslation.translator import TranslationOptions,register

@register(loi_18_07_consentement)
class SiteSettingTranslationOptions(TranslationOptions):
    fields = (
        'title',
        'text',
        'read_button_text',
        'privacy_policy_title',
        'privacy_policy_page',
        'decline_button_text',
    )

@register(Wilaya)
class WilayaTranslation(TranslationOptions):
    fields = (
        'nom',
    )
@register(Agence)
class AgenceTranslation(TranslationOptions):
    fields = (
        'nom',
        'responsable',
        'adresse',
    )
@register(contactstInfos)
class AgenceTranslation(TranslationOptions):
    fields = (
        'adresse',
    )
