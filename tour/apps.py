from django.apps import AppConfig
from django.core.management import call_command

class TourConfig(AppConfig):
    name = "tour"
    labels = "my.tour"

    def ready(self):
        print('Running ready method in OrderFeedbackConfig...')
        
        # Call the management command to delete old orders
        call_command('update_tour_status')