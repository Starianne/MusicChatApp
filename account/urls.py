from django.urls import path
from . import views

urlpatterns = [
    path('', views.accountpage, name="account"),
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
]
