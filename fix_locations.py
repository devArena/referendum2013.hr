from referendum.models import Location

def fix_croatian_locations():
    for l in Location.objects.all():
        if l.country == 'Croatia' and l.county is None:
            l.fetch_county(force=True)
            print l.id


