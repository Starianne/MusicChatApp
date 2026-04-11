from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url="/goSignIn")
def homepage(request):
    return render (request, "home.html")


def go_sign_in_view(request):
    return render (request, "goSignIn.html")