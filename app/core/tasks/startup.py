from datetime import datetime, timedelta

from apscheduler.triggers.interval import IntervalTrigger

from app.core import logger
from app.core.scheduler import scheduler
from app.core.tasks.fetch_data_from_krisha import fetch_krisha


async def start_scheduler():
    if scheduler.running:
        logger.info("ℹ️ Scheduler уже запущен.")
        return

    try:
        scheduler.add_job(
            func=fetch_krisha,
            trigger=IntervalTrigger(days=2),
            id="backup_payment_db",
            name="Real-Estate-Analysis",
            coalesce=True,
            max_instances=1,
            misfire_grace_time=60,
            replace_existing=True,
            next_run_time=datetime.now() + timedelta(minutes=2),
        )
        scheduler.start()
        logger.info("Scheduler успешно запущен.")
    except Exception as e:
        logger.exception(f"Ошибка при запуске scheduler: {e}")
