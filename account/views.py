from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


#i think i put the spotify stuff here for now
from dotenv import load_dotenv
import os
#getting things that shouldn't be committed
load_dotenv()

import spotipy
from spotipy.oauth2 import SpotifyOAuth


def accountpage(request):
    return render (request, "account/account.html")

def register_view(request): 
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('/account/login')
        
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
            messages.info(request, 'Username or Password is incorrect')
    context = {}
    return render (request, "account/login.html",context)

def callback_view(request): #will use later
    return HttpResponse(request, "Boo")

def spotifyapipage_view(request):
    sp= spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id = os.getenv("CLIENT_ID"),
            client_secret = os.getenv("CLIENT_SECRET"),
            redirect_uri = 'http://127.0.0.1:8000/account/callback',
            scope='user-top-read'
        )
    )
    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " - ", track['name'])
    return HttpResponse (request, print(sp))