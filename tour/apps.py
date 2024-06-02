from django.apps import AppConfig
from django.core.management import call_command

class TourConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "tour"

    def ready(self):
        from tour.scheduler.tour_scheduler import start_scheduler
        start_scheduler()    