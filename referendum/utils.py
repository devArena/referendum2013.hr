from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import connection
from django.db.models import Count

from referendum.models import ActiveVote
from referendum import tasks

def calculate_percentages(counts, digits=2):
    '''
    Calculate percentages, given a list of counts.
    It sensibly rounds them, so the sum of all percentages is guaranteed to be 100.

    Exception: all counts are 0.

    >>> calculate_percentages([3, 1])
    [75, 25]
    >>> calculate_percentages([35, 1])
    [97, 3]
    >>> calculate_percentages([35, 1], digits=3)
    [972, 28]
    >>> calculate_percentages([1023, 432])
    [70, 30]
    >>> calculate_percentages([1023, 432], digits=4)
    [7031, 2969]
    >>> calculate_percentages([32, 124, 81, 45])
    [11, 44, 29, 16]
    >>> calculate_percentages([0, 0])
    [0, 0]
    >>> calculate_percentages([0])
    [0]
    '''
    total = sum(counts)
    precision = 10**digits

    if total == 0:
        return [0] * len(counts)

    whole = [precision * x // total for x in counts]
    leftover = [(precision * counts[i] % total, i) for i in range(len(counts))]

    assigned = sum(whole)
    leftover.sort()
    leftover.reverse()
    i = 0
    while assigned < precision:
        if counts[leftover[i][1]] > 0:
            whole[leftover[i][1]] += 1
            assigned += 1
        i += 1
        if i == len(counts):
            i = 0
    return whole

#TODO napisi dekorator @cache_value
def get_active_vote(facebook_id, force=False):
    '''
    Gets the active vote of a particular facebook user.
    '''
    key = 'vote_{}'.format(facebook_id)
    vote = cache.get(key)
    if vote is None or force:
        try:
            vote = ActiveVote.objects.get(facebook_id=facebook_id)
        except ObjectDoesNotExist:
            vote = None
        except MultipleObjectsReturned:
            vote = tasks.fix_votes(facebook_id)
        cache.set(key, vote)
    return vote

def get_global_results(force=False):
    '''
    Gets the global results from cache.

    If there are no results, we calculate them and save to cache.
    '''
    key = 'global_results'
    result = cache.get(key)
    if result is None or force:
        query_result = ActiveVote.objects.values('vote').annotate(Count('vote'))
        result = [0] * 2
        for q in query_result:
            result[q['vote']] = q['vote__count']
        cache.set(key, result)
    return result

def get_global_count(force=False):
    '''
    Gets the total number of votes casted.
    '''
    return sum(get_global_results(force))

def get_friends_results(user_id, force=False):
    '''
    Gets the results for facebook friends of the user.

    If there are no results, we calculate them and save to cache.
    '''
    key = 'friends_{}'.format(user_id)
    result = cache.get(key)
    if result is None or force:
        cursor = connection.cursor()
        cursor.execute(
            'SELECT vote, COUNT(vote) ' +
                'FROM django_facebook_facebookuser AS fb ' +
                'JOIN referendum_activevote AS v ' +
                    'ON fb.facebook_id = v.facebook_id ' +
                'WHERE fb.user_id=%s ' +
                'GROUP BY vote',
            [user_id]
        )
        results_raw = cursor.fetchall()
        result = [0] * 2
        for r in results_raw:
            result[r[0]] = int(r[1])
        cache.set(key, result)
    return result

def get_full_results(user_id, force=False):
    ret = {}

    friends_results = get_friends_results(user_id, force)
    ret['friends_results'] = {
        'percentages': calculate_percentages(friends_results),
        'raw_numbers': friends_results,
        'responses': sum(friends_results),
    }

#TODO: add results by age
    global_results = get_global_results(force)
    ret['global_results'] = {
        'percentages': calculate_percentages(global_results),
        'raw_numbers': global_results,
        'responses': sum(global_results)
    }

    return ret

def get_georesults(scope, location, force=False):
    if scope != 'county' and scope != 'country':
        raise KeyError('scope value incorrect!')
    if location != 'current' and location != 'hometown':
        raise KeyError('location value incorrect!')
    # our database is stupid
    if location == 'current':
        location = 'location'

    key = 'georesults_{}_{}'.format(scope, location)
    results = cache.get(key)
    if results is None or force:
        query_string = (
            'SELECT l.{0}, av.vote, count(*)' +
            '  FROM referendum_activevote AS av' +
            '  JOIN referendum_facebookuserwithlocation AS u' +
            '    ON u.facebook_id = av.facebook_id' +
            '  JOIN referendum_location AS l' +
            '    ON l.id = u.{1}_id' +
            '  GROUP BY' +
            '    l.{0}, av.vote'
        ).format(scope, location)
        
        cursor = connection.cursor()
        cursor.execute(query_string)
        raw_results = cursor.fetchall()

        results = {}
        for result in raw_results:
            (place, vote, count) = result
            if place not in results:
                results[place] = [0] * 2
            results[place][vote] = count

        cache.set(key, results)
    return results


#TODO: couple this query with query for glabal results
def get_global_ageresults(force=False):
    '''
    Gets the global results per age from cache.

    If there are no results, we calculate them and save to cache.
    '''
    key = 'glabal_ageresults'
    result = cache.get(key)
    if result is None or force:
        #do this better using django CRM or postgres CTE
        cursor = connection.cursor()
        #format this nicely
        cursor.execute(
                       'SELECT av.vote, '+
                       'CASE'+
                       "   WHEN (date_part('years',AGE(fb.date_of_birth))<10 ) THEN 0"+
                       "   WHEN (date_part('years',AGE(fb.date_of_birth))<20) THEN 1"+
                       "   WHEN (date_part('years',AGE(fb.date_of_birth))<30) THEN 2"+
                       "   WHEN (date_part('years',AGE(fb.date_of_birth))<40) THEN 3"+
                       "   WHEN (date_part('years',AGE(fb.date_of_birth))<50) THEN 4"+
                       "   WHEN (date_part('years',AGE(fb.date_of_birth))<60)  THEN 5"+
                       "   WHEN (date_part('years',AGE(fb.date_of_birth))>=60) THEN 6"+
                       '   ELSE 7' +
                       '   END AS decade,'+
                       '   COUNT(av.vote)'+
                      '   FROM referendum_facebookuserwithlocation AS fb'+
                      '   JOIN referendum_activevote AS av'+
                      '   ON fb.facebook_id = av.facebook_id'+
                      #'   WHERE fb.date_of_birth IS NOT NULL'+
                      '   GROUP BY decade, av.vote'+
                      '   ORDER BY decade, av.vote')
        results_raw = cursor.fetchall()
        
        #TODO: do this on client side or prepare sql
        #TODO: [Important!] use calculate_percentages to overcome anonymity issues?
        bins = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60+', 'Nepoznato']
        no_yes = ['PROTIV', 'ZA']
        result = []
        
        for bin in bins:
            result.append({'godine': bin, 'ZA': 0, 'PROTIV':0})
        for r in results_raw:
            result[r[1]][no_yes[r[0]]]=r[2]

        cache.set(key, result)
        
    return result

if __name__ == '__main__':
    import doctest
    doctest.testmod()

