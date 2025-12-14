from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from app.features.schedule_training.job import register_jobs

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

def start_scheduler():
    if not scheduler.running:
        register_jobs(scheduler)
        scheduler.start()
        logger.info("Scheduler started")