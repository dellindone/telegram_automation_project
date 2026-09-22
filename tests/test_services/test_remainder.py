import pandas as pd

from src.config.sheets import ReminderColumn, ReminderConfigColumn, SubscriptionColumn
from src.models.remainder import ReminderStatus
from src.services.remainder import ReminderService


def test_get_enabled_configs():
    df = pd.DataFrame([{ReminderConfigColumn.ID: 1, ReminderConfigColumn.REMINDER_DAYS: 7, ReminderConfigColumn.ENABLED: "TRUE"}, {ReminderConfigColumn.ID: 2, ReminderConfigColumn.REMINDER_DAYS: 3, ReminderConfigColumn.ENABLED: "FALSE"}, {ReminderConfigColumn.ID: 3, ReminderConfigColumn.REMINDER_DAYS: 1, ReminderConfigColumn.ENABLED: "TRUE"}])
    result = ReminderService.get_enabled_configs(df)
    assert len(result) == 2
    assert list(result[ReminderConfigColumn.REMINDER_DAYS]) == [7, 1]


def test_get_next_reminder_id_when_empty():
    assert ReminderService.get_next_reminder_id(pd.DataFrame()) == 1


def test_get_next_reminder_id():
    df = pd.DataFrame([{ReminderColumn.ID: 1}, {ReminderColumn.ID: 5}, {ReminderColumn.ID: 3}])
    assert ReminderService.get_next_reminder_id(df) == 6


def test_reminder_exists():
    df = pd.DataFrame([{ReminderColumn.ID: 1, ReminderColumn.SUBSCRIPTION_ID: 10, ReminderColumn.REMINDER_DAYS: 7}])
    assert bool(ReminderService.reminder_exists(df, 10, 7)) is True
    assert bool(ReminderService.reminder_exists(df, 10, 3)) is False


def test_reminder_exists_when_empty():
    assert ReminderService.reminder_exists(pd.DataFrame(), 10, 7) is False


def test_build_reminder():
    scheduled_date = pd.Timestamp("2026-09-24").date()
    result = ReminderService.build_reminder(reminder_id=1, subscription_id=10, reminder_days=7, scheduled_date=scheduled_date)
    assert result[ReminderColumn.ID] == 1
    assert result[ReminderColumn.SUBSCRIPTION_ID] == 10
    assert result[ReminderColumn.REMINDER_DAYS] == 7
    assert result[ReminderColumn.SCHEDULED_DATE] == scheduled_date
    assert result[ReminderColumn.SENT_AT] == ""
    assert result[ReminderColumn.STATUS] == ReminderStatus.PENDING
    assert result[ReminderColumn.ERROR] == ""


def test_process_subscription_creates_reminders():
    subscription = pd.Series({SubscriptionColumn.ID: 10, SubscriptionColumn.STATUS: "active", SubscriptionColumn.EXPIRY_DATE: "2026-10-01"})
    configs = pd.DataFrame([{ReminderConfigColumn.REMINDER_DAYS: 7}, {ReminderConfigColumn.REMINDER_DAYS: 3}])
    reminders_df = pd.DataFrame()
    reminders, next_id = ReminderService.process_subscription(subscription, configs, reminders_df, 1)
    assert len(reminders) == 2
    assert reminders[0][ReminderColumn.ID] == 1
    assert reminders[0][ReminderColumn.REMINDER_DAYS] == 7
    assert reminders[0][ReminderColumn.SCHEDULED_DATE].isoformat() == "2026-09-24"
    assert reminders[1][ReminderColumn.ID] == 2
    assert reminders[1][ReminderColumn.REMINDER_DAYS] == 3
    assert reminders[1][ReminderColumn.SCHEDULED_DATE].isoformat() == "2026-09-28"
    assert next_id == 3


def test_process_subscription_skips_inactive_subscription():
    subscription = pd.Series({SubscriptionColumn.ID: 10, SubscriptionColumn.STATUS: "removed", SubscriptionColumn.EXPIRY_DATE: "2026-10-01"})
    configs = pd.DataFrame([{ReminderConfigColumn.REMINDER_DAYS: 7}])
    reminders, next_id = ReminderService.process_subscription(subscription, configs, pd.DataFrame(), 1)
    assert reminders == []
    assert next_id == 1


def test_process_subscription_skips_existing_reminder():
    subscription = pd.Series({SubscriptionColumn.ID: 10, SubscriptionColumn.STATUS: "active", SubscriptionColumn.EXPIRY_DATE: "2026-10-01"})
    configs = pd.DataFrame([{ReminderConfigColumn.REMINDER_DAYS: 7}, {ReminderConfigColumn.REMINDER_DAYS: 3}])
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1, ReminderColumn.SUBSCRIPTION_ID: 10, ReminderColumn.REMINDER_DAYS: 7}])
    reminders, next_id = ReminderService.process_subscription(subscription, configs, reminders_df, 2)
    assert len(reminders) == 1
    assert reminders[0][ReminderColumn.REMINDER_DAYS] == 3
    assert next_id == 3


def test_create_reminders():
    subscriptions_df = pd.DataFrame([{SubscriptionColumn.ID: 10, SubscriptionColumn.STATUS: "active", SubscriptionColumn.EXPIRY_DATE: "2026-10-01"}])
    reminders_df = pd.DataFrame()
    config_df = pd.DataFrame([{ReminderConfigColumn.ID: 1, ReminderConfigColumn.REMINDER_DAYS: 7, ReminderConfigColumn.ENABLED: "TRUE"}, {ReminderConfigColumn.ID: 2, ReminderConfigColumn.REMINDER_DAYS: 3, ReminderConfigColumn.ENABLED: "FALSE"}])
    result = ReminderService.create_reminders(subscriptions_df, reminders_df, config_df)
    assert len(result) == 1
    assert result.iloc[0][ReminderColumn.SUBSCRIPTION_ID] == 10
    assert result.iloc[0][ReminderColumn.REMINDER_DAYS] == 7


def test_create_reminders_with_no_enabled_configs():
    subscriptions_df = pd.DataFrame([{SubscriptionColumn.ID: 10, SubscriptionColumn.STATUS: "active", SubscriptionColumn.EXPIRY_DATE: "2026-10-01"}])
    config_df = pd.DataFrame([{ReminderConfigColumn.ID: 1, ReminderConfigColumn.REMINDER_DAYS: 7, ReminderConfigColumn.ENABLED: "FALSE"}])
    result = ReminderService.create_reminders(subscriptions_df, pd.DataFrame(), config_df)
    assert result.empty