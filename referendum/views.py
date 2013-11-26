import ast
import datetime
import json
import random
import re
import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.http import require_http_methods

from referendum import tasks
from referendum.models import ActiveVote, FacebookUserWithLocation, Vote
from referendum.utils import *

from project.settings import USE_CELERY

from django_facebook.decorators import facebook_required_lazy

def example(request):
    user = request.user
    context = RequestContext(request)
    context['votes_count'] = get_global_count()

    if user.is_authenticated():
        vote = get_active_vote(user.facebook_id)
        if vote is None:
            context['vote'] = -1
        else:
            context['vote'] = vote.vote
        full_results = get_full_results(user.id)
        context.update(full_results)
        return render_to_response('main.html', context)
    else:
        context['vote'] = -1
        return render_to_response('logged_out.html', context)

@login_required
@require_http_methods(["POST"])
def vote(request):

    if not request.user.is_authenticated():
        raise PermissionDenied

    vote = -1

    try:
        vote = int(request.POST['vote'])
        if vote < 0 or vote > 1 :
            return HttpResponseBadRequest('ERROR 400')
        if USE_CELERY:
            tasks.save_vote.delay(request.user.facebook_id, vote)
        else:
            tasks.save_vote(request.user.facebook_id, vote)
    except (KeyError, ValueError) as e:
        return HttpResponseBadRequest('ERROR 400')

    return HttpResponse(vote)

def local_map(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/?from=croatia')
    context = RequestContext(request)
    return render_to_response('map-local.html', context)

def world_map(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/?from=world')
    context = RequestContext(request)
    return render_to_response('map.html', context)

def fetch_country_data(request, scope, location):
    if not request.user.is_authenticated():
        raise PermissionDenied

    georesults = get_georesults(scope, location)

    results = [['Podrucje', 'Postotak ZA']]
    for place in georesults:
        total = sum(georesults[place])
        if total < 5: continue
        percentages = calculate_percentages(georesults[place])
        results.append([place, percentages[1]])

    return HttpResponse(json.dumps(results))


