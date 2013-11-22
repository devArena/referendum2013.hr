import datetime

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
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
    if not request.user.is_authenticated():
        raise PermissionDenied
    key = 'global_results'
    result = cache.get(key)
    if result is None:
        result = '{}'.format(ActiveVote.objects.values('vote').annotate(Count('vote')))
        cache.set(key, result)
    return HttpResponse(result)

def friends_results(request):
    #TODO: vrati JSON
    #TODO: napravi ovo bolje
    if not request.user.is_authenticated():
        raise PermissionDenied
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

def stressTest(request):
	userList=range(1,30001)
	random.shuffle(userList)
	num_friends=random.randint(1,500)
	user_id=random.randint(1,30000)
	username='netkoinesto'
	first_name='firstname'
	last_name='lastname'
	email='email'
	password='password'
	last_login=datetime.datetime.now()

	us=User													                       	 	 (id = 1, username=username,first_name=first_name,last_name=last_name,email=email,password=password,
	is_staff=0,is_active=1,is_superuser=0,last_login=last_login,date_joined=last_login)	
	friends=[]

	for i in range(1, num_friends+1):
	 	facebook_id=random.randint(10000,300000)
		gender=random.randint(1,2)
		name='PERO'
		gend='male'
		if gender==2:
			gend='female'
		friend_dict = { "id":facebook_id, "uid":facebook_id,  "name":name, "sex":gend }

		#friend=FacebookUser(user_id=user_id,facebook_id=facebook_id, name=name,gender=gend)
		#friend.save()
		friends.append(friend_dict)
	
	
	choice=random.randint(0,1)
	date=datetime.datetime.now()
	v=Vote(vote=choice,date=date,facebook_id=facebook_id)
	v.save()
 	#for f in friends:
	f = friends[0]
	print f.get('name')
	store_friends(us,friends)
	return HttpResponseRedirect(reverse('referendum:example'))
	#return render_to_response('referendum/example.html')
    
