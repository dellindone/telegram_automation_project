from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd
import pytest
from src.config.sheets import SheetName, ReminderColumn


@patch("src.processes.send_remainder.ReminderSendingService.send_due_reminders")
@pytest.mark.asyncio
async def test_send_reminders(mock_send_due_reminders):
    from src.processes.send_remainder import send_reminders

    sheets = MagicMock()
    telegram = MagicMock()

    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1}])
    subscriptions_df = pd.DataFrame([{"id": 10}])
    members_df = pd.DataFrame([{"id": 20}])
    updated_reminders_df = reminders_df.copy()

    sheets.get_sheet_as_dataframe.side_effect = [
        reminders_df,
        subscriptions_df,
        members_df,
    ]
    mock_send_due_reminders.return_value = updated_reminders_df

    await send_reminders(sheets, telegram)

    assert sheets.get_sheet_as_dataframe.call_count == 3
    mock_send_due_reminders.assert_awaited_once_with(
        reminders_df=reminders_df,
        subscriptions_df=subscriptions_df,
        members_df=members_df,
        telegram=telegram,
    )
    sheets.update_changed_rows.assert_called_once_with(
        sheet_name=SheetName.REMINDERS,
        old_df=reminders_df,
        new_df=updated_reminders_df,
    )