from referendum.models import Location

def fix_croatian_locations():
    for l in Location.objects.all():
        if l.country == 'Croatia':
            print '{} is in {}'.format(l.name, l.fetch_county())
        else:
            print '-- {}'.format(l.name)

