from datetime import date
from enum import StrEnum

from pydantic import BaseModel


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REMOVAL_PENDING = "removal_pending"
    REMOVED = "removed"
    REMOVAL_FAILED = "removal_failed"
    CANCELLED = "cancelled"


class Subscription(BaseModel):
    id: int
    member_id: int
    subscribe_date: date
    expired_after: int
    expiry_date: date | None = None
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    removed_at: date | None = None
    error: str | None = None