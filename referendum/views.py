from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
import datetime
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
    print ActiveVote.objects.values('vote').annotate(Count('vote'))
    return HttpResponseRedirect(reverse('referendum:example'))

def friend_results(request):
    pass

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
