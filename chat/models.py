from django.db import models
from django.contrib.auth.models import User

class MatchQueue(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_user2")

    room_name = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1} + {self.user2}"
    

class UserBlocked(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocker")
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_user")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked_user")
