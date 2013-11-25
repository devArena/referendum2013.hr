from django.core.cache import cache
from django.db import connection
from django.db.models import Count

from referendum.models import ActiveVote

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


def get_global_results():
    '''
    Gets the global results from cache.

    If there are no results, we calculate them and save to cache.
    '''
    key = 'global_results_2'
    result = cache.get(key)
    if result is None:
        result = ActiveVote.objects.values('vote').annotate(Count('vote'))
        cache.set(key, result)
    return result

def get_friends_results(user_id):
    '''
    Gets the results for facebook friends of the user.

    If there are no results, we calculate them and save to cache.
    '''
    key = 'friends_{}_2'.format(user_id)
    result = cache.get(key)
    if result is None:
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
        result = cursor.fetchall()
        cache.set(key, result)
    return result

def get_percentages(user_id):
    global_results_raw = get_global_results()
    friends_results_raw = get_friends_results(user_id)

    global_results = [0] * 2
    friends_results = [0] * 2

    for g in global_results_raw:
        global_results[g['vote']] = g['vote__count']
    for f in friends_results_raw:
        friends_results[f[0]] = f[1]

    friends_percentages = calculate_percentages(friends_results)
    global_percentages = calculate_percentages(global_results)
    return (friends_percentages, global_percentages)


if __name__ == '__main__':
    import doctest
    doctest.testmod()


