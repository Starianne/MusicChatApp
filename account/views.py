from django.shortcuts import render, redirect

from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from dotenv import load_dotenv
from .models import Song, UserTopSongs

import requests
import json
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
            new_user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
            login(request, new_user)
            return redirect('/account/match') #change this to match later
        
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


from django.http import JsonResponse

#nope @csrf_exempt
def get_selection(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request, how did you not POST this?"}, status=400)
    
    try:
        data = json.loads(request.body)
        song_list = data['song_list'] 
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Invalid request, there was an error"}, status=400)
    #csrf_token bug
    for song in song_list:
        song_id = song["songId"]
        song_obj, created = Song.objects.get_or_create(
            deezer_id = song_id,
            defaults={
                "name" : song["songTitle"],
                "album_art" : song["songImg"],
                "artist" : song["songArtist"]
            }
        )

        UserTopSongs.objects.get_or_create(
            user = request.user,
            song = song_obj
        )

            #store ts in the model
    
    #add to user top song model

    return JsonResponse({'message': f'You selected: {song_list} and they are saved'})



def song_search_view(request):
    if request.method == 'GET':
        searched_song = request.GET.get('song')
        if searched_song == None:
            results = None
        else:
            url = f"https://api.deezer.com/search?q={searched_song}"
            response = requests.get(url)
            data = response.json()
            if list(data.items())[0][0] == 'error': #no items will return error
                results = None
                messages.error(request, 'You have to enter a Song!')
            else:
                results = data["data"][:10]
    return render (request, "account/songSearch.html", {"results": results})

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