from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("find/", views.join_matchmaking, name="find_match"),
    path("check_match/", views.check_match, name="check_match"),
    path("<int:chat_id>/", views.room, name="room"),
]
