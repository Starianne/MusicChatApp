from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("load_chat_from_match/", views.load_chat_from_match, name="load_chat_from_match"),
    path("<int:chat_id>/", views.room, name="room"),
    path("none_found/", views.none_found_view, name="none_found"),
    path("matching/", views.matching_view, name="matching"),
]
