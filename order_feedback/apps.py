from django.apps import AppConfig
from django.core.management import call_command

class OrderFeedbackConfig(AppConfig):
    name = 'order_feedback'

    def ready(self):
        print('Running ready method in OrderFeedbackConfig...')
        
        # Call the management command to delete old orders
        call_command('delete_old_orders')
