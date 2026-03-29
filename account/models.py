from django.db import models
from django.contrib.auth.models import User
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
    #user + 5 songs as foreign keys