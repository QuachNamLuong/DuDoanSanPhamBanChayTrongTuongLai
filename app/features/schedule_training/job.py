from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .handler import train_model_handler

def register_jobs(scheduler: AsyncIOScheduler):
    scheduler.add_job(
        train_model_handler,
        trigger="cron",
        month="1,4,7,10",
        day=1,
        hour=0,
        minute=0,
        # Test
        # trigger="interval",
        # seconds=10,
        id="quarterly_model_training",
        replace_existing=True,
    )
