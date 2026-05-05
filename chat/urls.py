from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("load_chat_from_match/", views.load_chat_from_match, name="load_chat_from_match"),
    path("<int:chat_id>/", views.room, name="room"),
    path("<int:chat_id>/leave/", views.leave_chat, name="leave_chat"),
    path("<int:chat_id>/accept/", views.accept_chat, name="accept_chat"),
    path("none_found/", views.none_found_view, name="none_found"),
    path("matching/", views.matching_view, name="matching"),
    path("my_chats/", views.my_chats, name="my_chats"),
    path("search_users/", views.search_users, name="search_users"),
    path("force_match/", views.force_match, name="force_match"),  
]
