from enum import StrEnum


class SheetName(StrEnum):
    MEMBERS = "members"
    SUBSCRIPTIONS = "subscriptions"
    REMINDERS = "reminders"
    REMINDER_CONFIG = "reminder_config"

class MemberColumn(StrEnum):
    ID = "id"
    TELEGRAM_USER_ID = "telegram_user_id"
    NAME = "name"
    STATUS = "status"
    JOINED_DATE = "joined_date"


class SubscriptionColumn(StrEnum):
    ID = "id"
    MEMBER_ID = "member_id"
    SUBSCRIBE_DATE = "subscribe_date"
    EXPIRED_AFTER = "expired_after"
    EXPIRY_DATE = "expiry_date"
    STATUS = "status"
    REMOVED_AT = "removed_at"
    ERROR = "error"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class ReminderColumn(StrEnum):
    ID = "id"
    SUBSCRIPTION_ID = "subscription_id"
    REMINDER_DAYS = "reminder_days"
    SCHEDULED_DATE = "scheduled_date"
    SENT_AT = "sent_at"
    STATUS = "status"
    ERROR = "error"

class ReminderConfigColumn(StrEnum):
    ID = "id"
    REMINDER_DAYS = "reminder_days"
    ENABLED = "enabled"
