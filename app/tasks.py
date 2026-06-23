import random
from app.celery_app import celery_app

@celery_app.task(
    name="app.tasks.send_notification",
    bind=True,
    max_retries=3,
)
def send_notification(self, notification_id: str, recipient_email: str, channel: str, message: str):
    try:
        print(f"Sending {channel} notification to {recipient_email}")
        print(f"Message: {message}")
        print(f"Notification ID: {notification_id}")
        return {"status": "sent", "notification_id": notification_id}
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            dead_letter_task.delay(
                notification_id=notification_id,
                recipient_email=recipient_email,
                channel=channel,
                message=message,
                error=str(exc)
            )
            return {"status": "dead_lettered", "notification_id": notification_id}
        
        base_delay = 2 ** self.request.retries
        jitter = random.uniform(0, 1)
        raise self.retry(exc=exc, countdown=base_delay + jitter)


@celery_app.task(name="app.tasks.dead_letter_task", queue="dead_letter")
def dead_letter_task(notification_id: str, recipient_email: str, channel: str, message: str, error: str):
    print(f"❌ DEAD LETTER — Notification {notification_id} failed permanently")
    print(f"   Recipient: {recipient_email}")
    print(f"   Channel: {channel}")
    print(f"   Error: {error}")