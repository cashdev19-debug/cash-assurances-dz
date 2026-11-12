from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from django.shortcuts import render
from wagtail.models import Page, Locale
from wagtail.documents import get_document_model
from .models import SearchPageText
from django.conf import settings
Document = get_document_model()

def search(request):
    search_query = request.GET.get("query", "").strip()
    page = request.GET.get("page", 1)
    available_languages = settings.LANGUAGES
    page_results = Page.objects.none()
    doc_results = []
    search_settings = SearchPageText.load()
    if search_query:
        locale = Locale.get_active()
        page_results = Page.objects.live().public().filter(locale=locale).search(search_query)
        doc_results = Document.objects.search(search_query)

    paginator = Paginator(page_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    context = {
        "search_query": search_query,
        "search_results": search_results,
        "doc_results": doc_results,
        "search_settings": search_settings,
        "available_languages": available_languages,
    }

    return TemplateResponse(
        request,
        "search/search.html",
        context,
    )

