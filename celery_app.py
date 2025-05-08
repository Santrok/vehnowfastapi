from celery import Celery

import settings

celery_app = Celery(
    'tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['celery_tasks'],
)

celery_app.conf.update(
    broker_connection_max_retries = 3,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Europe/Moscow',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240 ,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_timeout=30,
    worker_concurrency=4,
    worker_max_tasks_per_child=100,
    task_always_eager=False,
    worker_pool_restarts=True,
    worker_cancel_long_running_tasks_on_connection_loss=True,
    broker_connection_retry_on_startup=True,
    worker_max_memory_per_child=250000,
)

