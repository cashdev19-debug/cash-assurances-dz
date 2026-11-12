# chatbot/urls.py
from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("api/chat/", views.chat_api, name="chat_api"),
    path("api/history/", views.history_api, name="history_api"),
    path("api/suggestions/", views.suggestions_api, name="suggestions_api"),
]