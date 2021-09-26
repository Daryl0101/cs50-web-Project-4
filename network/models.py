from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    like = models.ManyToManyField('Post', blank=True, related_name='likes')
    following = models.ManyToManyField('User', blank=True, related_name='followers')

class Post(models.Model):
    content = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=CASCADE, related_name='posts')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.content}'
