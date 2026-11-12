from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from wagtail.models import Locale
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.translation import get_language
from wagtail.models import Page, Locale 
from wagtail.documents.models import Document


@require_POST
def acceptConsent(request): 
    request.session['has_consented_terms'] = True
    return HttpResponse("Consentement enregistré pour 2 semaines.")


@require_POST
def declineConsent(request):    
    request.session['has_consented_terms'] = False
    return HttpResponse("Consentement enregistré pour 2 semaines.")

def cash_search(request):
    search_query = request.GET.get("q", None)
    page = request.GET.get("page", 1)
    doc_results = []
    # Search live, public Wagtail pages in the current language locale
    if search_query:
        locale = Locale.get_active()
        search_results = (
            Page.objects.live()
            .public()
            .filter(locale=locale)
            .search(search_query)
        )
        doc_results = Document.objects.search(search_query)[:5]
    else:
        search_results = Page.objects.none()

    paginator = Paginator(search_results, 8)
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
    }
    # HTMX DETECTOR: Return partial HTML when typed in the modal
    if request.headers.get("HX-Request"):
        return render(request, "includes/header.html#searchResult", context)

    # Normal full page render (when visiting /search/ directly)
    return render(request, "includes/header.html#searchResult", context)