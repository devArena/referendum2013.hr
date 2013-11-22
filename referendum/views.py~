import datetime

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.models import Count
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from project.settings import CACHE_TIMEOUT
from referendum.models import Vote, ActiveVote

def example(request):
    context = RequestContext(request)
    if request.user.is_authenticated():
        #TODO: makni filter
        votes = Vote.objects.filter(facebook_id=request.user.facebook_id).order_by('-date')
        if len(votes) >= 1:
            vote = votes[0]
        else:
            vote = None
    else:
        vote = None
    context['vote'] = vote
    return render_to_response('referendum/example.html', context)

def results(request):
    #TODO: vrati JSON
    #TODO: napravi ovo bolje
    key = 'global_results'
    result = cache.get(key)
    if result is None:
        result = '{}'.format(ActiveVote.objects.values('vote').annotate(Count('vote')))
        cache.set(key, result)
    return HttpResponse(result)

def friends_results(request):
    #TODO: vrati JSON
    #TODO: napravi ovo bolje
    key = 'friends_{}'.format(request.user.id)
    result = cache.get(key)
    if result is None:
        cursor = connection.cursor()
        cursor.execute(
            ('SELECT vote, COUNT(vote) ' +
                'FROM django_facebook_facebookuser AS fb ' +
                'JOIN referendum_activevote AS v ' +
                    'ON fb.facebook_id = v.facebook_id ' +
                'WHERE fb.user_id={} ' +
                'GROUP BY vote')
            .format(request.user.id)
        )
        result = '{}'.format(cursor.fetchall())
        cache.set(key, result)
    return HttpResponse(result)

def vote(request, facebook_id):
    #TODO: saniteze post
    now = datetime.datetime.now()
    #TODO: provjeri je li korisnik prijavljen...
    v = Vote(vote=request.POST['choice'],facebook_id=request.user.facebook_id)
    v.save()
    try:
        active_vote = ActiveVote.objects.get(facebook_id=request.user.facebook_id)
        active_vote.vote = request.POST['choice']
    except ObjectDoesNotExist:
        active_vote = ActiveVote(
            vote=request.POST['choice'],
            facebook_id=request.user.facebook_id
        )
    active_vote.save()
    return HttpResponseRedirect(reverse('referendum:example'))
