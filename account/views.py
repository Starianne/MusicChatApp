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
        #else: #add error messages tomorrow for register and log in views
            #if not form.cleaned_data["username"] : #ts probably isnt right
                #pass
        
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
            messages.error(request, 'Username or Password is incorrect')
    return render (request, "account/login.html")

def logout_view(request):
    logout(request)
    return redirect('/account/login') #must have first / to redirect properly

def search_view(request):
    if request.method == 'GET':
        searched_track = request.GET.get('track')
        if searched_track == None:
            results = None
        else:
            url = f"https://api.deezer.com/search?q={searched_track}"
            response = requests.get(url)
            data = response.json()
            if list(data.items())[0][0] == 'error':
                results = None
                messages.error(request, 'You have to enter a Song!')
            else:
                results = data["data"][:10]
    return render (request, "account/search.html", {"results": results})

def artist_search_view(request):
    if request.method == 'GET':
        searched_artist = request.GET.get('artist')
        if searched_artist == None:
            results = None
        else:
            url = f"https://api.deezer.com/search/artist?q={searched_artist}"
            response = requests.get(url)
            data = response.json()
            if list(data.items())[0][0] == 'error':
                results = None
                messages.error(request, 'You have to enter an Artist!')
            else:
                results = data["data"][:10]
    return render (request, "account/artistSearch.html", {"results": results})

def match_view(request):
    return render (request, 'account/match.html')