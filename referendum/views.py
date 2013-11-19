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
    return render_to_response('referendum/example.html', context)

def vote(request, facebook_id):
    now = datetime.datetime.now()
    v = Vote(vote=request.POST['choice'],date=now,facebook_id=facebook_id)
    v.save()
    return HttpResponseRedirect(reverse('referendum:example'))

