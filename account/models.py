from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Artist(models.Model):
    name = models.CharField(max_length=200)
    deezer_id = models.IntegerField(unique=True)

    def __str__(self):
        return self.name
    
class Track(models.Model):
    name = models.CharField(max_length=200)
    deezer_id = models.IntegerField(unique=True)
    album_art = models.URLField(blank=True)
    artist =  models.ForeignKey(Artist, on_delete=models.CASCADE)   

class UserTopArtists(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "artist")

    def __str__(self):
        return f"{self.user.username} - {self.artist.name}"
    
class UserTopTracks(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    track_artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "track", "track_artist")

    def __str__(self):
        return f"{self.user.username} - {self.track.name} by {self.track_artist.name}"
