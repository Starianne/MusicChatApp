from django.urls import path
from . import views

urlpatterns = [
    path('', views.testchat_view, name="testchat"),
]