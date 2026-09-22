from unittest.mock import AsyncMock

import pandas as pd
import pytest

from src.config.sheets import MemberColumn, ReminderColumn, SubscriptionColumn
from src.services.remainder_sending import ReminderSendingService


def test_get_due_reminders():
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1, ReminderColumn.SUBSCRIPTION_ID: 10, ReminderColumn.REMINDER_DAYS: 7, ReminderColumn.SCHEDULED_DATE: "2026-09-20", ReminderColumn.STATUS: "pending"}, {ReminderColumn.ID: 2, ReminderColumn.SUBSCRIPTION_ID: 11, ReminderColumn.REMINDER_DAYS: 3, ReminderColumn.SCHEDULED_DATE: "2099-01-01", ReminderColumn.STATUS: "pending"}, {ReminderColumn.ID: 3, ReminderColumn.SUBSCRIPTION_ID: 12, ReminderColumn.REMINDER_DAYS: 1, ReminderColumn.SCHEDULED_DATE: "2026-09-20", ReminderColumn.STATUS: "sent"}])
    result = ReminderSendingService.get_due_reminders(reminders_df)
    assert len(result) == 1
    assert result.iloc[0][ReminderColumn.ID] == 1


def test_build_expiry_message():
    result = ReminderSendingService.build_expiry_message("2026-10-01", 7)
    assert result == "Your Telegram group subscription will expire in 7 day(s) on 2026-10-01."


def test_get_telegram_user_id():
    subscription = pd.Series({SubscriptionColumn.MEMBER_ID: 10})
    members_df = pd.DataFrame([{MemberColumn.ID: 10, MemberColumn.TELEGRAM_USER_ID: 1090899134}])
    result = ReminderSendingService.get_telegram_user_id(subscription, members_df)
    assert result == 1090899134


def test_get_telegram_user_id_member_not_found():
    subscription = pd.Series({SubscriptionColumn.MEMBER_ID: 10})
    members_df = pd.DataFrame([{MemberColumn.ID: 20, MemberColumn.TELEGRAM_USER_ID: 1090899134}])
    with pytest.raises(ValueError, match="Member 10 not found"):
        ReminderSendingService.get_telegram_user_id(subscription, members_df)


@pytest.mark.asyncio
async def test_send_due_reminders_success():
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1, ReminderColumn.SUBSCRIPTION_ID: 10, ReminderColumn.REMINDER_DAYS: 7, ReminderColumn.SCHEDULED_DATE: "2026-09-20", ReminderColumn.STATUS: "pending", ReminderColumn.SENT_AT: "", ReminderColumn.ERROR: ""}])
    subscriptions_df = pd.DataFrame([{SubscriptionColumn.ID: 10, SubscriptionColumn.MEMBER_ID: 20, SubscriptionColumn.EXPIRY_DATE: "2026-10-01"}])
    members_df = pd.DataFrame([{MemberColumn.ID: 20, MemberColumn.TELEGRAM_USER_ID: 1090899134}])
    telegram = AsyncMock()
    result = await ReminderSendingService.send_due_reminders(reminders_df, subscriptions_df, members_df, telegram)
    assert result.loc[0, ReminderColumn.STATUS] == "sent"
    assert result.loc[0, ReminderColumn.SENT_AT] != ""
    telegram.send_message.assert_awaited_once_with(telegram_user_id=1090899134, message="Your Telegram group subscription will expire in 7 day(s) on 2026-10-01.")


@pytest.mark.asyncio
async def test_send_due_reminders_failure():
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1, ReminderColumn.SUBSCRIPTION_ID: 10, ReminderColumn.REMINDER_DAYS: 7, ReminderColumn.SCHEDULED_DATE: "2026-09-20", ReminderColumn.STATUS: "pending", ReminderColumn.SENT_AT: "", ReminderColumn.ERROR: ""}])
    subscriptions_df = pd.DataFrame([{SubscriptionColumn.ID: 10, SubscriptionColumn.MEMBER_ID: 20, SubscriptionColumn.EXPIRY_DATE: "2026-10-01"}])
    members_df = pd.DataFrame([{MemberColumn.ID: 20, MemberColumn.TELEGRAM_USER_ID: 1090899134}])
    telegram = AsyncMock()
    telegram.send_message.side_effect = RuntimeError("Telegram failed")
    result = await ReminderSendingService.send_due_reminders(reminders_df, subscriptions_df, members_df, telegram)
    assert result.loc[0, ReminderColumn.STATUS] == "failed"
    assert result.loc[0, ReminderColumn.ERROR] == "Telegram failed"


@pytest.mark.asyncio
async def test_send_due_reminders_subscription_not_found():
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1, ReminderColumn.SUBSCRIPTION_ID: 10, ReminderColumn.REMINDER_DAYS: 7, ReminderColumn.SCHEDULED_DATE: "2026-09-20", ReminderColumn.STATUS: "pending", ReminderColumn.SENT_AT: "", ReminderColumn.ERROR: ""}])
    subscriptions_df = pd.DataFrame(columns=[SubscriptionColumn.ID, SubscriptionColumn.MEMBER_ID, SubscriptionColumn.EXPIRY_DATE])
    members_df = pd.DataFrame([{MemberColumn.ID: 20, MemberColumn.TELEGRAM_USER_ID: 1090899134}])
    telegram = AsyncMock()
    result = await ReminderSendingService.send_due_reminders(reminders_df, subscriptions_df, members_df, telegram)
    assert result.loc[0, ReminderColumn.STATUS] == "failed"
    assert result.loc[0, ReminderColumn.ERROR] == "Subscription not found."


@pytest.mark.asyncio
async def test_send_due_reminders_member_not_found():
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1, ReminderColumn.SUBSCRIPTION_ID: 10, ReminderColumn.REMINDER_DAYS: 7, ReminderColumn.SCHEDULED_DATE: "2026-09-20", ReminderColumn.STATUS: "pending", ReminderColumn.SENT_AT: "", ReminderColumn.ERROR: ""}])
    subscriptions_df = pd.DataFrame([{SubscriptionColumn.ID: 10, SubscriptionColumn.MEMBER_ID: 20, SubscriptionColumn.EXPIRY_DATE: "2026-10-01"}])
    members_df = pd.DataFrame(columns=[MemberColumn.ID, MemberColumn.TELEGRAM_USER_ID])
    telegram = AsyncMock()
    result = await ReminderSendingService.send_due_reminders(reminders_df, subscriptions_df, members_df, telegram)
    assert result.loc[0, ReminderColumn.STATUS] == "failed"
    assert "Member 20 not found" in result.loc[0, ReminderColumn.ERROR]