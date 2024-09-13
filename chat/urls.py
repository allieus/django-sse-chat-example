from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.index, name="index"),
    path("chat/sse/", views.chat_sse, name="chat_sse"),
]
