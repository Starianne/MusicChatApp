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
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

CurrentUserModel= get_user_model()

def index(request):
    return render(request, "chat/index.html")


@login_required
def room(request, chat_id):
    #pass chat messages, sender user id and other_members id to room AND CHAT NAME + is group
    members = list(ChatMember.objects.filter(chat_id = chat_id).values("id", "user_id", "user__username", "role", "status"))
    messages = Message.objects.filter(chat_id=chat_id).select_related("sender").order_by('created_at')
    chat = Chat.objects.get(id = chat_id)
    return render(request, "chat/room.html",  {"chat_id": chat_id, "chat_name" : chat.name, "is_group": chat.is_group, "messages": messages, "current_user" : request.user.username, "members" : members})

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
        role = "admin",
        status="ACCEPTED"  #only for admin
    )

    for username in usernames:
        try:
            user = CurrentUserModel.objects.get(username = username)
            ChatMember.objects.get_or_create(chat = chat, user = user)
        except CurrentUserModel.DoesNotExist:
            continue

    return JsonResponse({"chat_id" : chat.id})

@require_POST
def add_member(request):
    data = json.loads(request.body)
    username = data["username"]
    chat_id = data["chat_id"]
    try:
        chat = Chat.objects.get(id=chat_id)
        user = CurrentUserModel.objects.get(username=username)
        ChatMember.objects.get_or_create(chat=chat, user=user)
        return JsonResponse({"ok": True})
    except CurrentUserModel.DoesNotExist:
        return JsonResponse({"ok": False, "error": "user not found"}, status=404)

@login_required
@require_POST
def leave_chat(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id)
        
        if chat.is_group: #if group only leave chat
            ChatMember.objects.filter(chat_id=chat_id, user=request.user).delete()
        else:
            #get other user to block
            other_member = ChatMember.objects.filter(
                chat_id=chat_id
            ).exclude(user=request.user).first()

            if other_member:
                #block both ways so neither match
                UserBlocked.objects.get_or_create(
                    blocker=request.user,
                    blocked_user=other_member.user
                )
                UserBlocked.objects.get_or_create(
                    blocker=other_member.user,
                    blocked_user=request.user
                )

            #broadcast to all users in the room before deleting
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{chat_id}",
                {"type": "chat.deleted"} #dots become underscores - maps to chat_deleted()
            )

            #delete match first so the onetoone becomes null before chat gets deleted
            Match.objects.filter(chat_id=chat_id).delete()
            Chat.objects.filter(id=chat_id).delete()
        
        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

@login_required
@require_POST
def accept_chat(request, chat_id):
    try:
        #update member status
        member = ChatMember.objects.get(chat_id=chat_id, user=request.user)
        member.status = "ACCEPTED"
        member.save()

        #update admin status to stop pending lock
        
        ChatMember.objects.filter(chat_id=chat_id, role="admin").update(status="ACCEPTED")
        
        #let everyone know that chat was accepted
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{chat_id}",
            {"type": "chat.accepted"}
        )
        return JsonResponse({"status": "ok"})
    
    except ChatMember.DoesNotExist:
        return JsonResponse({"status": "error", "message": "member not found"}, status=404)
    

#to display chat data
@login_required
def my_chats(request):
    #get chats + status
    memberships = ChatMember.objects.filter(
        user=request.user
    ).select_related("chat").order_by("-chat__created_at")

    accepted = []
    pending = []

    for m in memberships:
        chat = m.chat
        #get other user name for dms
        other_member = ChatMember.objects.filter(
            chat=chat
        ).exclude(user=request.user).select_related("user").first()

        last_message = Message.objects.filter(
            chat=chat
        ).order_by("-created_at").first()

        #fall back names incase there is so gc name or other user
        chat_data = {
            "chat_id": chat.id,
            "name": chat.name if chat.name else (other_member.user.username if other_member else "chat"),
            "is_group": chat.is_group,
            "last_message": last_message.content if last_message else None,
        }

        if m.status == "PENDING" and m.role == "member":
            pending.append(chat_data)
        elif m.status == "ACCEPTED":
            accepted.append(chat_data)

    return JsonResponse({"accepted": accepted, "pending": pending})

#for searchbar
@login_required
def search_users(request):
    query = request.GET.get("q", "").strip()
 
    if len(query) < 1:
        return JsonResponse({"users": []})
 
    #exclude people you already know
    blocked_users = UserBlocked.objects.filter(blocker=request.user).values_list("blocked_user_id", flat=True)
    blocked_by_users = UserBlocked.objects.filter(blocked_user=request.user).values_list("blocker_id", flat=True)
    matched_to = Match.objects.filter(user1=request.user).values_list("user2_id", flat=True)
    matched_by = Match.objects.filter(user2=request.user).values_list("user1_id", flat=True)
 
    excluded = list(blocked_users) + list(blocked_by_users) + list(matched_to) + list(matched_by) + [request.user.id]
 
    users = (
        CurrentUserModel.objects.filter(username__icontains=query)
        .exclude(id__in=excluded)
        .order_by("username")[:5]
    )
 
    return JsonResponse({
        "users": [{"id": u.id, "username": u.username} for u in users]
    })
 
#send user into match after pressing match
@login_required
@require_POST
def force_match(request):
    data = json.loads(request.body)
    target_id = data.get("target_user_id")
 
    target_user = CurrentUserModel.objects.get(id=target_id)
 
    #check match doesnt already exist
    already_matched = Match.objects.filter(
        Q(user1=request.user, user2=target_user) |
        Q(user1=target_user, user2=request.user)
    ).first()
 
    if already_matched:
        return JsonResponse({"chat_id": already_matched.chat.id})
 
    with transaction.atomic():
        match = Match.objects.create(
            user1=request.user,
            user2=target_user,
        )
 
        chat = Chat.objects.create(
            created_by=request.user,
            is_group=False,
        )
 
        ChatMember.objects.bulk_create([
            ChatMember(chat=chat, user=request.user, role="admin", status="ACCEPTED"),
            ChatMember(chat=chat, user=target_user, status="PENDING"),
        ])
 
        match.chat = chat
        match.save(update_fields=["chat"])
 
    return JsonResponse({"chat_id": chat.id})

#search for gcs
@login_required
def search_all_users(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 1:
        return JsonResponse({"users": []})

    blocked_users = UserBlocked.objects.filter(blocker=request.user).values_list("blocked_user_id", flat=True)
    blocked_by_users = UserBlocked.objects.filter(blocked_user=request.user).values_list("blocker_id", flat=True)

    excluded = list(blocked_users) + list(blocked_by_users) + [request.user.id]

    users = (
        CurrentUserModel.objects.filter(username__icontains=query)
        .exclude(id__in=excluded)
        .order_by("username")[:5]
    )
    return JsonResponse({
        "users": [{"id": u.id, "username": u.username} for u in users]
    })