from django.db import models
import datetime

class Vote(models.Model):
    facebook_id = models.BigIntegerField()
    vote = models.IntegerField()
    date = models.DateTimeField('voting date')

    def __unicode__(self):
        return self.name
