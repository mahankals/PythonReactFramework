from celery import Celery

from app.config import settings

celery_app = Celery(
    "sampleapp",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)

# Auto-discover tasks from app.tasks module
# Add task modules here as you create them:
celery_app.autodiscover_tasks(["app.tasks.email"])
