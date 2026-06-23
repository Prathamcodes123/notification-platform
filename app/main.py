
from fastapi import FastAPI, Depends
from pydantic import BaseModel, EmailStr
from enum import Enum
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app.models import Notification
from app.tasks import send_notification

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

class Channel(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"

class NotificationRequest(BaseModel):
    recipient_email: EmailStr
    channel: Channel
    subject: str
    message: str
    idempotency_key: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/notifications")
def create_notification(body: NotificationRequest, db: Session = Depends(get_db)):
    # 1. PEHLE check karo — duplicate hai kya?
    existing = db.query(Notification).filter(
        Notification.idempotency_key == body.idempotency_key
    ).first()
    
    if existing:
        return {
            "status": "already_queued",
            "id": str(existing.id),
            "channel": existing.channel,
            "recipient": existing.recipient_email,
        }

    # 2. TAB naya banao
    notification = Notification(
        recipient_email=body.recipient_email,
        channel=body.channel,
        subject=body.subject,
        message=body.message,
        idempotency_key=body.idempotency_key,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    send_notification.delay(
        notification_id=str(notification.id),
        recipient_email=notification.recipient_email,
        channel=notification.channel,
        message=notification.message
    )
    
    return {
        "status": "queued",
        "id": str(notification.id),
        "channel": notification.channel,
        "recipient": notification.recipient_email,
    }