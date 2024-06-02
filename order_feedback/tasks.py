from datetime import datetime
from django.utils import timezone
from order_feedback.models import Order

def delete_incomplete_orders():
    one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)
    incomplete_orders = Order.objects.filter(is_complete=False, date_time__lte=one_minute_ago)
    count = incomplete_orders.count()

    if count > 0:
        incomplete_orders.delete()
        print(f'Successfully deleted {count} incomplete orders older than 1 minute.')
    else:
        print('No incomplete orders older than 1 minute found.')