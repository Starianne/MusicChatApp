from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from dotenv import load_dotenv
import requests
#getting things that shouldn't be committed
load_dotenv()




def accountpage(request):
    return render (request, "account/account.html")

def register_view(request): 
    form = CreateUserForm() #sets up create user form
    if request.method == 'POST':
        form = CreateUserForm(request.POST) #renders form and passes in post data
        if form.is_valid():
            new_user = form.save() #makes user in database
            user_name = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user_name)
            new_user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
            login(request, new_user)
            return redirect('/') #change this to match later
        
    context = {'form':form} 
    return render (request, "account/register.html", context)

def login_view(request): 
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Usergname or Password is incorrect')
    return render (request, "account/login.html")

def logout_view(request):
    logout(request)
    return redirect('/account/login') #must have first / to redirect properly

def search_view(request):
    if request.method == 'GET':
        searched_track = request.GET.get('track')
        url = f"https://api.deezer.com/search?q={searched_track}"
        response = requests.get(url)
        data = response.json()
        results = data["data"][:5]
    return render (request, "account/search.html", {"results": results})

def match_view(request):
    return render (request, 'account/match.html')