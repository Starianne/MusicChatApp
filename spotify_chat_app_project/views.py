from django.shortcuts import render

def homepage(request):
    return render (request, "home.html")


def go_sign_in_view(request):
    return render (request, "goSignIn.html")