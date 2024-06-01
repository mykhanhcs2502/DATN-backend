# scheduler/apps.py
from django.apps import AppConfig

class SchedulerConfig(AppConfig):
    name = 'scheduler'

    def ready(self):
        from scheduler import tasks
        tasks.start()
