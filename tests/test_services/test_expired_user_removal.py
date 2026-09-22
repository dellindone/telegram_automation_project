from unittest.mock import AsyncMock

import pandas as pd
import pytest

from src.config.sheets import MemberColumn, ReminderColumn, SubscriptionColumn
from src.services.expired_user_removal import ExpiredUserRemovalService


@pytest.mark.asyncio
async def test_remove_expired_user_success():
    subscriptions_df = pd.DataFrame([{SubscriptionColumn.ID: 10, SubscriptionColumn.MEMBER_ID: 20, SubscriptionColumn.STATUS: "active", SubscriptionColumn.EXPIRY_DATE: "2026-09-20", SubscriptionColumn.REMOVED_AT: "", SubscriptionColumn.ERROR: ""}])
    members_df = pd.DataFrame([{MemberColumn.ID: 20, MemberColumn.TELEGRAM_USER_ID: 1090899134, MemberColumn.STATUS: "active"}])
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1, ReminderColumn.SUBSCRIPTION_ID: 10, ReminderColumn.REMINDER_DAYS: 7}])
    telegram = AsyncMock()

    result_subscriptions, result_members, result_reminders = await ExpiredUserRemovalService.remove_expired_users(subscriptions_df, members_df, reminders_df, telegram)

    assert result_subscriptions.loc[0, SubscriptionColumn.STATUS] == "removed"
    assert result_subscriptions.loc[0, SubscriptionColumn.REMOVED_AT] != ""
    assert result_members.loc[0, MemberColumn.STATUS] == "inactive"
    assert result_reminders.empty
    telegram.remove_user.assert_awaited_once_with(1090899134)


@pytest.mark.asyncio
async def test_remove_expired_user_failure():
    subscriptions_df = pd.DataFrame([{SubscriptionColumn.ID: 10, SubscriptionColumn.MEMBER_ID: 20, SubscriptionColumn.STATUS: "active", SubscriptionColumn.EXPIRY_DATE: "2026-09-20", SubscriptionColumn.REMOVED_AT: "", SubscriptionColumn.ERROR: ""}])
    members_df = pd.DataFrame([{MemberColumn.ID: 20, MemberColumn.TELEGRAM_USER_ID: 1090899134, MemberColumn.STATUS: "active"}])
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1, ReminderColumn.SUBSCRIPTION_ID: 10, ReminderColumn.REMINDER_DAYS: 7}])
    telegram = AsyncMock()
    telegram.remove_user.side_effect = RuntimeError("Telegram removal failed")

    result_subscriptions, result_members, result_reminders = await ExpiredUserRemovalService.remove_expired_users(subscriptions_df, members_df, reminders_df, telegram)

    assert result_subscriptions.loc[0, SubscriptionColumn.STATUS] == "removal_failed"
    assert "Telegram removal failed" in result_subscriptions.loc[0, SubscriptionColumn.ERROR]
    assert result_members.loc[0, MemberColumn.STATUS] == "active"
    assert len(result_reminders) == 1
    telegram.remove_user.assert_awaited_once_with(1090899134)


@pytest.mark.asyncio
async def test_active_subscription_is_not_removed():
    subscriptions_df = pd.DataFrame([{SubscriptionColumn.ID: 10, SubscriptionColumn.MEMBER_ID: 20, SubscriptionColumn.STATUS: "active", SubscriptionColumn.EXPIRY_DATE: "2099-10-01", SubscriptionColumn.REMOVED_AT: "", SubscriptionColumn.ERROR: ""}])
    members_df = pd.DataFrame([{MemberColumn.ID: 20, MemberColumn.TELEGRAM_USER_ID: 1090899134, MemberColumn.STATUS: "active"}])
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1, ReminderColumn.SUBSCRIPTION_ID: 10, ReminderColumn.REMINDER_DAYS: 7}])
    telegram = AsyncMock()

    result_subscriptions, result_members, result_reminders = await ExpiredUserRemovalService.remove_expired_users(subscriptions_df, members_df, reminders_df, telegram)

    assert result_subscriptions.loc[0, SubscriptionColumn.STATUS] == "active"
    assert result_members.loc[0, MemberColumn.STATUS] == "active"
    assert len(result_reminders) == 1
    telegram.remove_user.assert_not_awaited()