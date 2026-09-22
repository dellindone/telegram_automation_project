from unittest.mock import MagicMock, patch
import pandas as pd
from src.config.sheets import SheetName, ReminderColumn


@patch("src.processes.create_remainders.ReminderService.create_reminders")
def test_create_reminders(mock_create_reminders):
    from src.processes.create_remainders import create_reminders

    sheets = MagicMock()
    subscriptions_df = pd.DataFrame([{"id": 1, "status": "active"}])
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1}])
    reminder_config_df = pd.DataFrame([{"id": 1, "reminder_days": 7, "enabled": True}])
    new_reminders_df = pd.DataFrame([{ReminderColumn.ID: 2, ReminderColumn.SUBSCRIPTION_ID: 1}])

    sheets.get_sheet_as_dataframe.side_effect = [subscriptions_df, reminders_df, reminder_config_df]
    mock_create_reminders.return_value = new_reminders_df

    create_reminders(sheets)

    assert sheets.get_sheet_as_dataframe.call_count == 3
    mock_create_reminders.assert_called_once_with(
        subscriptions_df=subscriptions_df,
        reminders_df=reminders_df,
        reminder_config_df=reminder_config_df,
    )
    sheets.append_rows.assert_called_once_with(
        sheet_name=SheetName.REMINDERS,
        df=new_reminders_df,
    )


@patch("src.processes.create_remainders.ReminderService.create_reminders")
def test_create_reminders_when_no_new_reminders(mock_create_reminders):
    from src.processes.create_remainders import create_reminders

    sheets = MagicMock()
    subscriptions_df = pd.DataFrame([{"id": 1, "status": "active"}])
    reminders_df = pd.DataFrame([{ReminderColumn.ID: 1}])
    reminder_config_df = pd.DataFrame([{"id": 1, "reminder_days": 7, "enabled": True}])

    mock_create_reminders.return_value = pd.DataFrame()

    sheets.get_sheet_as_dataframe.side_effect = [subscriptions_df, reminders_df, reminder_config_df]

    create_reminders(sheets)

    mock_create_reminders.assert_called_once()
    sheets.append_rows.assert_not_called()

