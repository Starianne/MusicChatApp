from django.shortcuts import render
from django.http import HttpResponse

def accountpage(request):
    return HttpResponse("account page")

def register(request):
    return HttpResponse("registerpage")

def login(request):
    return HttpResponse("loginpage")