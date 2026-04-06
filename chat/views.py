from django.shortcuts import render
from account.models import UserTopSongs
import uuid
from django.db import transaction
from .models import MatchQueue, Match, UserBlocked
from django.http import JsonResponse
from django.db.models import Q

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
            "room":match.room_name
        })
    
    match = find_match(request.user)

    if match:
        print("second match before find")
        print(match)
        return JsonResponse({
            "matched":True,
            "room":match.room_name
        })
    
    print("final match that should be none")
    print(match)
    return JsonResponse({"matched": False})

