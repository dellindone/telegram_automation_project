from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

from src.config.settings import settings
from src.config.sheets import SheetName


class GoogleSheetsClient:
    """Client responsible for reading and updating Google Sheets."""
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets",]

    def __init__(self) -> None:
        print("Connecting to Google Sheets...")
        self.client = self._create_client()
        self.spreadsheet = self._get_sheet()
        print("Connected to Google Sheets.")

    def _create_client(self) -> gspread.Client:
        credentials = Credentials.from_service_account_file(settings.google_credentials_file, scopes=self.SCOPES,)
        return gspread.authorize(credentials)

    def _get_sheet(self) -> gspread.Worksheet:
        return self.client.open_by_key(settings.google_sheet_id)

    def get_sheet_as_dataframe(self, sheet_name: SheetName) -> pd.DataFrame:
        print(f"Fetching data from sheet: {sheet_name}")
        worksheet = self.spreadsheet.worksheet(sheet_name)
        records = worksheet.get_all_records()
        print(f"Fetched {len(records)} records from sheet: {sheet_name}")
        return pd.DataFrame(records)

    def update_sheet_from_dataframe(self, sheet_name: SheetName, df: pd.DataFrame,) -> None:
        print(f"Updating sheet: {sheet_name}")
        worksheet = self.spreadsheet.worksheet(sheet_name)
        data = [df.columns.tolist()] + df.fillna("").values.tolist()
        worksheet.clear()
        worksheet.update(range_name="A1", values=data,)
        print(f"Sheet {sheet_name} updated successfully.")

    def update_changed_rows(self, sheet_name: SheetName, old_df: pd.DataFrame, new_df: pd.DataFrame,) -> None:
        print(f"Updating changed rows in sheet: {sheet_name}")
        worksheet = self.spreadsheet.worksheet(sheet_name)
        if old_df.shape != new_df.shape: raise ValueError("Old and new DataFrame must have the same shape.")
        if list(old_df.columns) != list(new_df.columns): raise ValueError("Old and new DataFrame must have the same columns.")

        updates = []
        for row_index in range(len(old_df)):
            for column_index in range(len(old_df.columns)):
                old_value = old_df.iat[row_index, column_index]
                new_value = new_df.iat[row_index, column_index]

                old_empty = pd.isna(old_value) or old_value == ""
                new_empty = pd.isna(new_value) or new_value == ""

                if old_empty and new_empty: continue
                if str(old_value) == str(new_value): continue

                cell_row = row_index + 2
                cell_column = column_index + 1

                updates.append({
                        "range": gspread.utils.rowcol_to_a1(cell_row, cell_column,),
                        "values": [["" if new_empty else str(new_value)]],
                    }
                )

        if not updates: return
        worksheet.batch_update(updates)
        print(f"Updated {len(updates)} changed rows in sheet: {sheet_name}")

    def append_rows(self, sheet_name: SheetName, df: pd.DataFrame) -> None:
        if df.empty: return
        worksheet = self.spreadsheet.worksheet(sheet_name)
        values = df.fillna("").astype(str).values.tolist()
        worksheet.append_rows(values,value_input_option="USER_ENTERED",)
        print(f"Appended rows to sheet: {sheet_name}")
