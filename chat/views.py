from django.shortcuts import render
from account.models import UserTopSongs
import json
from django.db import transaction
from .models import *
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


CurrentUserModel= get_user_model()

def index(request):
    return render(request, "chat/index.html")

@login_required
def room(request, chat_id):
    #pass chat messages, sender user id and other_members id to room AND CHAT NAME
    members = list(ChatMember.objects.filter(chat_id = chat_id).values("id", "user_id", "user__username", "role", "status"))
    messages = Message.objects.filter(chat_id=chat_id).select_related("sender").order_by('created_at')
    chat_name = Chat.objects.get(id = chat_id).name
    print(f"this is the chatname: {chat_name}")
    return render(request, "chat/room.html",  {"chat_id": chat_id, "chat_name" : chat_name, "messages": messages, "current_user" : request.user.username, "members" : members})

def none_found_view(request):
    return render(request, "chat/none_found.html")

def matching_view(request):
    return render(request, "chat/matching.html")

#finds amount of songs shared between users
def shared_songs(user_a, user_b):
    songs_a = set(
        UserTopSongs.objects.filter(user=user_a).values_list("song_id", flat=True)
    )

    songs_b = set(
        UserTopSongs.objects.filter(user=user_b).values_list("song_id", flat=True)
    )

    return len(songs_a.intersection(songs_b))

def find_match(current_user):
    print(current_user.id)
    n = -1 #to increment through users
    found_match = None
    best_match = None
    best_score = -1

    blocked_users = UserBlocked.objects.filter(blocker = current_user.id).values_list("blocked_user_id", flat=True)
    blocked_by_users = UserBlocked.objects.filter(blocked_user = current_user.id).values_list("blocker_id", flat=True)
    matched_to = Match.objects.filter(user1 = current_user.id).values_list("user2_id", flat=True)
    matched_by = Match.objects.filter(user2 = current_user.id).values_list("user1_id", flat=True)

    excluded_users = list(blocked_users) + list(blocked_by_users) + list(matched_to) + list(matched_by)
    #filtered user list
    queued_users = CurrentUserModel.objects.exclude(username=current_user).exclude(id__in=excluded_users)

    last = len(queued_users)//10
    #go through filtered users to find match
    while not found_match:
        n += 1
        if n != (last + 1):
            user_batch = queued_users.order_by("id")[n * 10: n * 10 + 10]
            for user in user_batch:
                print(user)
                score = shared_songs(current_user, user)

                if score > best_score:
                    best_score = score
                    best_match = user
            
            if best_score > 0 :
                found_match = best_match

        else:
            return None
    
    #make chat + update match
    with transaction.atomic():

        match = Match.objects.create(
            user1=current_user,
            user2=best_match,
        )

        chat = Chat.objects.create(
            created_by = current_user,
            is_group=False,
        )

        ChatMember.objects.bulk_create([
            ChatMember(chat=chat, user=current_user, role="admin"),
            ChatMember(chat=chat, user=best_match),
        ])

        match.chat = chat
        match.save(update_fields=["chat"])

    return match

def load_chat_from_match(request):
    match = find_match(request.user)
    if match == None:
        return JsonResponse({
            "matched":False
        })
    else:
        return JsonResponse({
            "matched":True,
            "chat_id": match.chat.id,
        })



def check_match(request):
    match = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).first()

    if match:
        print("first match before find")
        print(match)
        print(match.chat.id)

    
    match = find_match(request.user)
    print(match)
    if match:
        print("second match before find")
        print(match)
        print(match.chat.id)
        return JsonResponse({
            "matched":True,
            "chat_id": match.chat.id,
        })
    
    print("final match that should be none")
    print(match)
    return JsonResponse({"matched": False})

@require_POST
def create_group_chat(request):
    data = json.loads(request.body)
    name = data.get("name", "")
    usernames = data.get("usernames", [])

    chat = Chat.objects.create(
        name = name,
        is_group = True,
        created_by = request.user,
    )

    ChatMember.objects.create(
        chat = chat,
        user = request.user,
        role = "admin"
    )

    for username in usernames:
        try:
            user = CurrentUserModel.objects.get(username = username)
            ChatMember.objects.get_or_create(chat = chat, user = user)
        except CurrentUserModel.DoesNotExist:
            continue

    return JsonResponse({"chat_id" : chat.id})

@require_POST
def add_member(request, chat_id):
    data = json.loads(request.body)
    username = data["username"]
    chat = Chat.objects.get(id = chat_id)
    user = CurrentUserModel.objects.get(username = username)
    
    ChatMember.objects.get_or_create(chat = chat, user = user)

    return JsonResponse({"ok" : True})