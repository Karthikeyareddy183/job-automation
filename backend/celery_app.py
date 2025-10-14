"""
Celery application configuration for background task processing
"""
from celery import Celery
from celery.schedules import crontab
from config.settings import settings

# Initialize Celery app
celery_app = Celery(
    "job_automation",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.scrape_jobs",
        "tasks.process_applications",
        "tasks.cleanup"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    task_soft_time_limit=25 * 60,  # Soft limit at 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Periodic task schedule using Celery Beat
celery_app.conf.beat_schedule = {
    # Scrape jobs every 6 hours
    "scrape-jobs-periodic": {
        "task": "tasks.scrape_jobs.scrape_all_job_boards",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours at :00
        "options": {"queue": "scraping"}
    },

    # Clean up old job postings daily
    "cleanup-old-jobs": {
        "task": "tasks.cleanup.cleanup_old_jobs",
        "schedule": crontab(minute=0, hour=2),  # Daily at 2 AM
        "options": {"queue": "maintenance"}
    },

    # Generate daily application report
    "daily-report": {
        "task": "tasks.process_applications.generate_daily_report",
        "schedule": crontab(minute=0, hour=18),  # Daily at 6 PM
        "options": {"queue": "reports"}
    },
}

# Task routing to different queues
celery_app.conf.task_routes = {
    "tasks.scrape_jobs.*": {"queue": "scraping"},
    "tasks.process_applications.*": {"queue": "applications"},
    "tasks.cleanup.*": {"queue": "maintenance"},
}

if __name__ == "__main__":
    celery_app.start()
