from django.db import models
import datetime

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

