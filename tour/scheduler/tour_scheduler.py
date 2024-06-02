from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from tour.tasks import update_tour_active
import logging
import atexit

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(
        update_tour_active,
        trigger=IntervalTrigger(minutes=1),
        id='update_tour_active',
        name='Update tour active if tour is completed',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started")

atexit.register(lambda: scheduler.shutdown())
