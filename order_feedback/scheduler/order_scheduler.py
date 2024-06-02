from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from order_feedback.tasks import delete_incomplete_orders
import logging
import atexit

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(
        delete_incomplete_orders,
        trigger=IntervalTrigger(minutes=1),
        id='delete_incomplete_orders',
        name='Delete incomplete orders older than 1 minute',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started")

atexit.register(lambda: scheduler.shutdown())
