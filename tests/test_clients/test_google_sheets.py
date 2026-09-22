from unittest.mock import MagicMock, patch

import pandas as pd

from src.config.sheets import SheetName


@patch("src.clients.google_sheets.gspread.authorize")
@patch("src.clients.google_sheets.Credentials.from_service_account_file")
def test_get_sheet_as_dataframe(mock_credentials, mock_authorize):
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_records.return_value = [{"id": 1, "name": "Aditya"}, {"id": 2, "name": "Rahul"}]

    mock_spreadsheet = MagicMock()
    mock_spreadsheet.worksheet.return_value = mock_worksheet

    mock_client = MagicMock()
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    from src.clients.google_sheets import GoogleSheetsClient

    sheets = GoogleSheetsClient()
    result = sheets.get_sheet_as_dataframe(SheetName.MEMBERS)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert result.iloc[0]["name"] == "Aditya"
    mock_spreadsheet.worksheet.assert_called_once_with(SheetName.MEMBERS)


@patch("src.clients.google_sheets.gspread.authorize")
@patch("src.clients.google_sheets.Credentials.from_service_account_file")
def test_append_rows(mock_credentials, mock_authorize):
    mock_worksheet = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_spreadsheet.worksheet.return_value = mock_worksheet

    mock_client = MagicMock()
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    from src.clients.google_sheets import GoogleSheetsClient

    sheets = GoogleSheetsClient()
    df = pd.DataFrame([{"id": 1, "name": "Aditya"}, {"id": 2, "name": "Rahul"}])

    sheets.append_rows(SheetName.MEMBERS, df)

    mock_worksheet.append_rows.assert_called_once_with([["1", "Aditya"], ["2", "Rahul"]], value_input_option="USER_ENTERED")


@patch("src.clients.google_sheets.gspread.authorize")
@patch("src.clients.google_sheets.Credentials.from_service_account_file")
def test_append_rows_does_nothing_when_empty(mock_credentials, mock_authorize):
    mock_spreadsheet = MagicMock()
    mock_client = MagicMock()
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    from src.clients.google_sheets import GoogleSheetsClient

    sheets = GoogleSheetsClient()
    sheets.append_rows(SheetName.MEMBERS, pd.DataFrame())

    mock_spreadsheet.worksheet.assert_not_called()


@patch("src.clients.google_sheets.gspread.authorize")
@patch("src.clients.google_sheets.Credentials.from_service_account_file")
def test_update_changed_rows(mock_credentials, mock_authorize):
    mock_worksheet = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_spreadsheet.worksheet.return_value = mock_worksheet

    mock_client = MagicMock()
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    from src.clients.google_sheets import GoogleSheetsClient

    sheets = GoogleSheetsClient()

    old_df = pd.DataFrame([{"id": 1, "status": "active"}])
    new_df = pd.DataFrame([{"id": 1, "status": "inactive"}])

    sheets.update_changed_rows(SheetName.MEMBERS, old_df, new_df)

    mock_worksheet.batch_update.assert_called_once()


@patch("src.clients.google_sheets.gspread.authorize")
@patch("src.clients.google_sheets.Credentials.from_service_account_file")
def test_update_changed_rows_does_not_update_when_no_changes(mock_credentials, mock_authorize):
    mock_worksheet = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_spreadsheet.worksheet.return_value = mock_worksheet

    mock_client = MagicMock()
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    from src.clients.google_sheets import GoogleSheetsClient

    sheets = GoogleSheetsClient()

    old_df = pd.DataFrame([{"id": 1, "status": "active"}])
    new_df = old_df.copy()

    sheets.update_changed_rows(SheetName.MEMBERS, old_df, new_df)

    mock_worksheet.batch_update.assert_not_called()