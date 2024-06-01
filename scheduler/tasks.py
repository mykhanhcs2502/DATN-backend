# from datetime import datetime, timedelta
# from apscheduler.schedulers.background import BackgroundScheduler
# from django_apscheduler.jobstores import DjangoJobStore, register_events
# from django.utils import timezone
# from django_apscheduler.models import DjangoJobExecution
# import sys
# from tour.models import Tour
# import logging

# # This is the function you want to schedule - add as many as you want and then register them in the start() function below
# def update_tours_status():
#     logging.info("Starting update_tours_status task...")
#     tours = Tour.objects.all()
#     for tour in tours:
#         if tour.starting_date + timedelta(days=tour.day_num) > datetime.now().date():
#             tour.isActive = False
#             tour.save()

#     logging.info(datetime.now().date())
#     return "Tours updated"

from datetime import datetime, timedelta
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from tour.models import Tour
import logging

def update_tours_status():
    logging.info("Starting update_tours_status task...")
    tours = Tour.objects.all()
    for tour in tours:
        if tour.starting_date + timedelta(days=tour.day_num) > datetime.now().date():
            tour.isActive = False
            tour.save()
    logging.info(datetime.now().date())
    return "Tours updated"

result = update_tours_status()
if result == "Tours updated":
    print("Task executed successfully.")

def start():
    print("Starting scheduler...")
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 24 hours
    scheduler.add_job(update_tours_status, 'interval', seconds=5, id='update_tours_status', replace_existing=True)
    register_events(scheduler)
    scheduler.start()
    # print("Scheduler started...", file=sys.stdout)