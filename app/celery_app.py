from celery import Celery

celery_app = Celery(
    "notification_platform",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0",
    include=["app.tasks"] 
)

celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "notifications"}
}

celery_app.conf.task_queues = {
    "notifications": {},
    "dead_letter": {}
}