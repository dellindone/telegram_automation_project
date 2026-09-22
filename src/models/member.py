from datetime import date
from enum import StrEnum

from pydantic import BaseModel


class MemberStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


class Member(BaseModel):
    id: int
    telegram_user_id: int
    name: str
    status: MemberStatus = MemberStatus.ACTIVE
    joined_date: date
    