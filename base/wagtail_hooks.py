from django.utils.html import format_html
from django.templatetags.static import static
from django.urls import path
from django.http import Http404
from django.shortcuts import get_object_or_404
from wagtail.models import Page
from wagtail_flexible_forms.models import StreamFormMixin
from wagtail import hooks
from wagtail.contrib.forms.models import FormMixin
from wagtailcache.cache import clear_cache

@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static('css/custom_admin.css'))


#@hooks.register("register_icons")
#def register_custom_icons(icons):
    # The path starts inside your app's template directory
#    return icons + [
#        "wagtailadmin/icons/bootstrap-icons.svg",
#    ]
@hooks.register('register_icons')
def replace_icons(icons):
    return icons + [
        "wagtailadmin/icons/bootstrap-icons.svg",
    ]


def flexible_form_submissions(request, *args, **kwargs):
    page_id = kwargs.get("page_id")
    form_page = get_object_or_404(Page, id=page_id).specific
    if not isinstance(form_page, StreamFormMixin) and not isinstance(form_page,FormMixin):
        raise Http404
    return form_page.serve_submissions_list_view(request, *args, **kwargs)

 

@hooks.register('register_admin_urls')
def register_flexible_form_submissions_url():
    return [
        path(
            'forms/submissions/<int:page_id>/',
            flexible_form_submissions,
            name='wagtailforms_list_submissions',
        ),
    ]
    
@hooks.register('construct_homepage_context')
def check_first_visit(request, context):
    first_visit = not request.COOKIES.get('has_visited')
    context['has_visited'] = first_visit
    
    
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.snippets.models import register_snippet as reg
from chatbot.models import ChatSession, InsuranceQA,InsuranceTopic



class InsuranceQAViewSet(SnippetViewSet):
    model = InsuranceQA
    icon = "help"
    menu_label = "Q&A Pairs"
    list_display = ["question", "topic", "locale", "priority", "is_active"]
    search_fields = ["question", "answer", "keywords"]

    def get_queryset(self, request):
        # Explicitly query the model to prevent NoneType errors, then optimize for SQL Server
        return self.model.objects.all().select_related("topic", "locale").prefetch_related("question_variants", "links").distinct()

class InsuranceTopicViewSet(SnippetViewSet):
    model = InsuranceTopic
    icon = "folder"
    menu_label = "Topics"
    list_display = ["name", "slug", "locale"]

    def get_queryset(self, request):
        return self.model.objects.all().select_related("locale").distinct()

class ChatSessionViewSet(SnippetViewSet):
    model = ChatSession
    icon = "comment"
    menu_label = "Chat Sessions & Transcripts"
    list_display = ["id", "created_at", "last_seen_at", "ip_address", "is_closed"]
    search_fields = ["id", "user_agent", "ip_address"]
    list_per_page = 20

class ChatbotAdminGroup(SnippetViewSetGroup):
    menu_label = "Chatbot"
    menu_icon = "cogs"
    menu_order = 200
    items = (InsuranceQAViewSet, InsuranceTopicViewSet, ChatSessionViewSet)

register_snippet(ChatbotAdminGroup)




@hooks.register('after_publish_page')
def clear_cache_on_publish(request, page):
    clear_cache()


@hooks.register('after_unpublish_page')
def clear_cache_on_unpublish(request, page):
    clear_cache()


@hooks.register('after_delete_page')
def clear_cache_on_delete(request, page):
    clear_cache()