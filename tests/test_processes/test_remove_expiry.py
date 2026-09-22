from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd
import pytest
from src.config.sheets import SheetName, SubscriptionColumn, MemberColumn, ReminderColumn


@patch("src.processes.remove_expiry.ExpiredUserRemovalService.remove_expired_users")
@pytest.mark.asyncio
async def test_remove_expired_users(mock_remove_expired_users):
    from src.processes.remove_expiry import remove_expired_users

    sheets = MagicMock()
    telegram = MagicMock()

    subscriptions_df = pd.DataFrame([{SubscriptionColumn.ID: 10}])
    members_df = pd.DataFrame([{MemberColumn.ID: 20}])
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1}])

    updated_subscriptions_df = subscriptions_df.copy()
    updated_members_df = members_df.copy()
    updated_reminders_df = reminders_df.copy()

    sheets.get_sheet_as_dataframe.side_effect = [
        subscriptions_df,
        members_df,
        reminders_df,
    ]

    mock_remove_expired_users.return_value = (
        updated_subscriptions_df,
        updated_members_df,
        updated_reminders_df,
    )

    await remove_expired_users(sheets, telegram)

    assert sheets.get_sheet_as_dataframe.call_count == 3
    mock_remove_expired_users.assert_awaited_once_with(
        subscriptions_df=subscriptions_df,
        members_df=members_df,
        reminders_df=reminders_df,
        telegram=telegram,
    )

    sheets.update_changed_rows.assert_any_call(
        sheet_name=SheetName.SUBSCRIPTIONS,
        old_df=subscriptions_df,
        new_df=updated_subscriptions_df,
    )

    sheets.update_changed_rows.assert_any_call(
        sheet_name=SheetName.MEMBERS,
        old_df=members_df,
        new_df=updated_members_df,
    )