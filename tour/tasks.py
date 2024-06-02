import datetime
from django.utils import timezone
from tour.models import Tour

def update_tour_active():
    tourset = Tour.objects.filter(isActive=True)
    for tour in tourset:
        date_check = tour.starting_date + datetime.timedelta(days=tour.day_num)
        if timezone.now().date() > date_check:
            tour.isActive = False
            # tour.save()

    print("All tour has been checked")
