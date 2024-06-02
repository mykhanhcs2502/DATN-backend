from django.apps import AppConfig

class OrderFeedbackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'order_feedback'

    def ready(self):
        from order_feedback.scheduler.order_scheduler import start_scheduler
        start_scheduler()
        
