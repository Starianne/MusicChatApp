from django.db import models
from django.conf import settings
# Create your models here.
    
class Song(models.Model):
    name = models.CharField(max_length=200)
    deezer_id = models.IntegerField(unique=True)
    album_art = models.URLField(blank=True)
    artist =  models.CharField(max_length=200)   

    def __str__(self):
        return f"{self.name} has Deezer ID {self.deezer_id} and was writen by {self.artist}"
    
    class Meta:
        unique_together = ("name", "deezer_id", "album_art", "artist")

class UserTopSongs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_top_songs")
    song = models.ForeignKey("Song", on_delete=models.CASCADE, null=True)
    rank = models.IntegerField()

    class Meta:
        unique_together = ("user", "rank") #otherwise you have multiple songs at rank 1 