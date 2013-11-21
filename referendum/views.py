from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
import datetime
from referendum.models import Vote

def example(request):
    context = RequestContext(request)
    if request.user.is_authenticated():
        #TODO: makni filter
        vote = Vote.objects.filter(facebook_id=request.user.facebook_id).order_by('-date')[0]
    else:
        vote = None
    context['vote'] = vote
    return render_to_response('referendum/example.html', context)

def vote(request, facebook_id):
    now = datetime.datetime.now()
    #TODO: provjeri je li korisnik prijavljen...
    v = Vote(vote=request.POST['choice'],facebook_id=request.user.facebook_id)
    v.save()
    return HttpResponseRedirect(reverse('referendum:example'))

