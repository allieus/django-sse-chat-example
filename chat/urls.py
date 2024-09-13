from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.index, name="index"),
    path("chat_messages/", views.chat_messages, name="chat_messages"),
    path("chat_message_new/", views.chat_message_new, name="chat_message_new"),
]
