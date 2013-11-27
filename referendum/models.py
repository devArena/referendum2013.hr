from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_facebook.models import FacebookModel, get_user_model
from django_facebook.utils import get_profile_model
from open_facebook.api import *

import urllib2

class Location(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    geolocation_api_response = models.TextField(blank=True, default=None, null=True)
    county = models.CharField(max_length=255, default=None, null=True)

    def __unicode__(self):
        return '{} ({},{})'.format(self.name, self.latitude, self.longitude)

    def fetch_county(self, force=False):
        if not force and self.county:
            return self.county
        geodata_json = self.fetch_geolocation_data(force)
        geodata_dict = json.loads(geodata_json)
        for result in geodata_dict['results']:
            if 'administrative_area_level_1' in result['types']:
                self.county = result['formatted_address']
                break
        if self.county is not None:
            self.save()
        else:
            # ovo je neki error...
            pass
        return self.county

    def fetch_geolocation_data(self, force=False):
        if not force and self.geolocation_api_response is not None:
            return self.geolocation_api_response
        url = self.api_endpoint()
        data = urllib2.urlopen(url).read()
        self.geolocation_api_response = data
        self.save()
        return self.geolocation_api_response

    def api_endpoint(self):
        URL = 'http://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&sensor=false'
        return URL.format(self.latitude, self.longitude)

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
    fetched_location = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.facebook_id is not None and self.access_token is not None and not self.fetched_location:
            query = 'SELECT hometown_location, current_location FROM user WHERE uid = {}'.format(self.facebook_id)
            facebook = OpenFacebook(self.access_token)
            result = facebook.fql(query)[0]
            self.location = Location.from_result(result['current_location'])
            self.hometown = Location.from_result(result['hometown_location'])
            self.fetched_location = True
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

