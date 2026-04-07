from django.shortcuts import render
from account.models import UserTopSongs
import uuid
import json
from django.db import transaction
from .models import *
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

User = get_user_model()

def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    return render(request, "chat/room.html",  {"room_name":room_name})

def shared_songs(user_a, user_b):
    songs_a = set(
        UserTopSongs.objects.filter(user=user_a).values_list("song_id", flat=True)
    )

    songs_b = set(
        UserTopSongs.objects.filter(user=user_b).values_list("song_id", flat=True)
    )

    return len(songs_a.intersection(songs_b))

def find_match(current_user):
    #error in this function?
    blocked_users = UserBlocked.objects.filter(blocker = current_user).values_list("blocked_user_id", flat=True)
    blocked_by_users = UserBlocked.objects.filter(blocked_user = current_user).values_list("blocker_id", flat=True)

    excluded_users = list(blocked_users) + list(blocked_by_users)

    queued_users = MatchQueue.objects.exclude(user=current_user).exclude(user_id__in=excluded_users)
    
    best_match = None
    best_score = -1

    for queued in queued_users:
        score = shared_songs(current_user, queued.user)

        if score > best_score:
            best_score = score
            best_match = queued.user

    if not best_match:
        return None
    
    with transaction.atomic():
        room_name = f"match_{uuid.uuid4().hex[:10]}"

        match = Match.objects.create(
            user1=current_user,
            user2=best_match,
            room_name=room_name
        )

        chat = Chat.objects.create(
            created_by = current_user,
            is_group=False,
        )

        ChatMember.objects.bulk_create([
            ChatMember(chat=chat, user=current_user),
            ChatMember(chat=chat, user=best_match),
        ])

        match.chat = chat
        match.save(update_fields=["chat"])

        MatchQueue.objects.filter(user=current_user).delete()
        MatchQueue.objects.filter(user=best_match).delete()

    return match


def join_matchmaking(request):
    MatchQueue.objects.get_or_create(user=request.user)

    return render(request, "chat/matching.html")

def check_match(request):
    match = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).first()
#i think bug may be here
    if match:
        print("first match before find")
        print(match)
        return JsonResponse({
            "matched":True,
            "room":match.room_name,
            "chat_id": match.chat.id,
        })
    
    match = find_match(request.user)

    if match:
        print("second match before find")
        print(match)
        return JsonResponse({
            "matched":True,
            "room":match.room_name,
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
            user = User.objects.get(username = username)
            ChatMember.objects.get_or_create(chat = chat, user = user)
        except User.DoesNotExist:
            continue

    return JsonResponse({"chat_id" : chat.id})

@require_POST
def add_member(request, chat_id):
    data = json.loads(request.body)
    username = data["username"]
    chat = Chat.objects.get(id = chat_id)
    user = User.objects.get(username = username)
    
    ChatMember.objects.get_or_create(chat = chat, user = user)

    return JsonResponse({"ok" : True})