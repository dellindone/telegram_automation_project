from datetime import date
from enum import StrEnum

from pydantic import BaseModel


class ReminderStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Reminder(BaseModel):
    id: int
    subscription_id: int
    reminder_days: int
    scheduled_date: date
    sent_at: date | None = None
    status: ReminderStatus = ReminderStatus.PENDING
    error: str | None = None
    