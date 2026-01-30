from django.shortcuts import render
from django.http import HttpResponse

def accountpage(request):
    return render (request, "account/account.html")

def register(request):
    return render (request, "account/register.html")

def login(request):
    return render (request, "account/login.html")