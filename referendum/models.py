from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_facebook.models import FacebookModel, get_user_model
from django_facebook.utils import get_profile_model
from open_facebook.api import *

class Location(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class FacebookUserWithLocation(AbstractUser, FacebookModel):
    objects = UserManager()
    location = models.ForeignKey(Location, blank=True, null=True, related_name='+')
    hometown = models.ForeignKey(Location, blank=True, null=True, related_name='+')


@receiver(post_save)
def create_profile(sender, instance, created, **kwargs):
    if sender == get_user_model():
        user = instance
        if user.facebook_id is not None:
            query = 'SELECT hometown_location, current_location FROM user WHERE uid = {}'.format(user.facebook_id)
            print user.access_token
            facebook = OpenFacebook(user.access_token)
            print facebook.fql(query)


class Vote(models.Model):
    facebook_id = models.BigIntegerField()
    vote = models.IntegerField()
    date = models.DateTimeField('voting date', auto_now_add=True)
    visible = models.BooleanField(default=True)
    eligible = models.BooleanField(default=True)

    def __unicode__(self):
        return '{}: {}'.format(self.facebook_id, self.vote)

    class Meta:
        ordering = ['-date']

class ActiveVote(models.Model):
    facebook_id = models.BigIntegerField()
    vote = models.IntegerField()

    def __unicode__(self):
        return '{}: {}'.format(self.facebook_id, self.vote)

