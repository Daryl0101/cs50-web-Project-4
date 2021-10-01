from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.deletion import CASCADE
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, pre_save


class User(AbstractUser):
    like = models.ManyToManyField('Post', blank=True, related_name='likes')
    following = models.ManyToManyField('User', blank=True, related_name='followers')

@receiver(m2m_changed, sender=User.following.through)
def validate_follow(sender, instance, pk_set, action, **kwargs):
    if action == 'post_add':
        if instance.pk in pk_set:
            raise ValidationError("Cannot follow yourself")



class Post(models.Model):
    content = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=CASCADE, related_name='posts')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.content}'
