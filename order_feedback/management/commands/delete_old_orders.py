import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from order_feedback.models import Order

class Command(BaseCommand):
    help = 'Deletes orders that are not complete and are older than 2 days'

    def handle(self, *args, **kwargs):
        self.stdout.write('Running delete_old_orders command...')

        threshold_date = timezone.now() - datetime.timedelta(minutes=1)

        old_orders = Order.objects.filter(is_complete=False, date_time__lt=threshold_date)

        count, _ = old_orders.delete()

        self.stdout.write(f'Successfully deleted {count} old incomplete orders.')
