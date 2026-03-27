from django.urls import path
from . import views

urlpatterns = [
    path('', views.accountpage, name="account"),
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('get_selection/', views.get_selection, name="get_selection"),
    path('songSearch/', views.song_search_view, name="songSearch"),
    path('artistSearch/', views.artist_search_view, name="artistSearch"),
    path('match/', views.match_view, name="match"),
]
