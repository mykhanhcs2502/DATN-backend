import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from tour.models import Tour

class Command(BaseCommand):
    help = 'Deletes orders that are not complete and are older than 2 days'

    def handle(self, *args, **kwargs):
        self.stdout.write('Running delete_old_orders command...')

        tourset = Tour.objects.filter(isActive=True)
        for tour in tourset:
            date_check = tour.starting_date + datetime.timedelta(days=tour.day_num)
            if timezone.now().date() > date_check:
                tour.isActive = False
                # tour.save()

        self.stdout.write(f'Successfully tour status.')
