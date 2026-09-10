import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.core.management import call_command

logger = logging.getLogger(__name__)

_scheduler = None


def _run_import_news():
    try:
        call_command("import_news")
    except Exception:
        logger.exception("Scheduled news import failed.")


def start():
    global _scheduler

    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler(timezone="UTC")

    _scheduler.add_job(
        _run_import_news,
        trigger=IntervalTrigger(hours=1),
        id="hourly_news_import",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    _scheduler.start()

    logger.info("News import scheduler started: refreshing every hour.")
