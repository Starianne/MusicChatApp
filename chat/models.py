from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class MatchQueue(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class UserBlocked(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocker")
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_user")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked_user")

class ChatMember(models.Model):
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("chat", "user")

class Chat(models.Model):
    name = models.CharField(max_length=120, blank=True)
    is_group = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_chats")
    created_at = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(User, through="ChatMember", related_name="chats")


    def __str__(self):
        return self.name or f"Chat {self.id}"
    


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

  
class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_user2")

    room_name = models.CharField(max_length=100, unique=True)
    chat = models.OneToOneField(Chat, null=True, blank=True, on_delete=models.SET_NULL, related_name="match")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1} + {self.user2}"