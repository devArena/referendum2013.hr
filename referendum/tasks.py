from __future__ import absolute_import

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from project.celery import app

from referendum.models import ActiveVote, Vote, FacebookUserWithLocation

def fix_votes(facebook_id):
    all_my_active_votes = ActiveVote.objects.filter(facebook_id=facebook_id)
    if len(all_my_active_votes) == 0:
        return None
    if len(all_my_active_votes) == 1:
        return all_my_active_votes[0]
    all_my_active_votes.all().delete()

    cache.delete('global_results')
    selected_vote = Vote.objects.filter(facebook_id=facebook_id).order_by('-date')[0]
    new_active_vote = ActiveVote(vote=selected_vote.vote, facebook_id=facebook_id)
    new_active_vote.save()
    return new_active_vote

@app.task
def save_vote(facebook_id, vote):
    try:
        user = FacebookUserWithLocation.objects.get(facebook_id=facebook_id)
    except ObjectDoesNotExist:
        return
    v = Vote(vote=vote, facebook_id=facebook_id)
    v.save()
    try:
        av = ActiveVote.objects.get(facebook_id=facebook_id)
        av.vote = vote
    except ObjectDoesNotExist:
        av = ActiveVote(vote=vote, facebook_id=facebook_id)
    except MultipleObjectsReturned:
        av = fix_votes(facebook_id)
        av.vote = vote
    av.save()

    keys = []
    keys.append('vote_{}'.format(facebook_id))
    keys.append('global_results')
    cache.delete_many(keys)

