from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_email = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    idempotency_key = Column(String, unique=True, nullable=False)
    status = Column(String, default="queued")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))