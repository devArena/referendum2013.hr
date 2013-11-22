from __future__ import absolute_import

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from project.celery import app

from referendum.models import ActiveVote, Vote

@app.task
def add(x, y):
    return x + y

@app.task
def mul(x, y):
    return x * y

@app.task
def xsum(numbers):
    return sum(numbers)

@app.task
def save_vote(facebook_id, vote):
    v = Vote(vote=vote, facebook_id=facebook_id)
    v.save()
    try:
        av = ActiveVote.objects.get(facebook_id=facebook_id)
        av.vote = vote
    except ObjectDoesNotExist:
        av = ActiveVote(vote=vote, facebook_id=facebook_id)
    av.save()

