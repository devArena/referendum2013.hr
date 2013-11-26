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
    if vote is None or foce:
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
    if result is None or fprce:
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

    global_results = get_global_results(force)
    ret['global_results'] = {
        'percentages': calculate_percentages(global_results),
        'raw_numbers': global_results,
        'responses': sum(global_results)
    }

    return ret


if __name__ == '__main__':
    import doctest
    doctest.testmod()

