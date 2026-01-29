from django.urls import path
from . import views

urlpatterns = [
    path('', views.accountpage),
    path('register/', views.register),
    path('login/', views.login),
]
