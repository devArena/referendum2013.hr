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
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __unicode__(self):
        return '{} ({},{})'.format(self.name, self.latitude, self.longitude)

    @classmethod
    def from_result(cls, data):
        if data is None:
            return None
        try:
            return cls.objects.get(id=data['id'])
        except cls.DoesNotExist:
            o = cls(
                id=data['id'],
                name=data['name'],
                city=data['city'],
                country=data['country'],
                zip=data['zip'],
                latitude=data['latitude'],
                longitude=data['longitude'],
            )
            o.save()
            return o


class FacebookUserWithLocation(AbstractUser, FacebookModel):
    objects = UserManager()
    location = models.ForeignKey(Location, blank=True, null=True, related_name='+')
    hometown = models.ForeignKey(Location, blank=True, null=True, related_name='+')

    def save(self, *args, **kwargs):
        if self.facebook_id is not None and self.access_token is not None and self.location is None:
            query = 'SELECT hometown_location, current_location FROM user WHERE uid = {}'.format(self.facebook_id)
            facebook = OpenFacebook(self.access_token)
            result = facebook.fql(query)[0]
            self.location = Location.from_result(result['current_location'])
            self.hometown = Location.from_result(result['hometown_location'])
        super(FacebookUserWithLocation, self).save(*args, **kwargs)


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

