from django.shortcuts import render
from django.http import HttpResponse


#i think i put the spotify stuff here for now
from dotenv import load_dotenv
import os
#getting things that shouldn't be committed
load_dotenv()

import spotipy
from spotipy.oauth2 import SpotifyOAuth


def accountpage(request):
    return render (request, "account/account.html")

def register(request):
    
    return render (request, "account/register.html")

def login(request):
    return render (request, "account/login.html")

def callback(request): #will use later
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