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
        if not records:
            headers = worksheet.row_values(1)
            return pd.DataFrame(columns=headers)
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

    def sync_dataframe_to_sheet(
        self, sheet_name: SheetName, old_df: pd.DataFrame,
        new_df: pd.DataFrame, key_column: str,
    ) -> None:
        """
        Diff old_df vs new_df by key_column and apply the minimal set of
        changes to the sheet: cell updates for changed existing rows,
        appended rows for new keys, and deleted rows for removed keys.
        """
        if list(old_df.columns) != list(new_df.columns):
            raise ValueError("Old and new DataFrame must have the same columns.")

        worksheet = self.spreadsheet.worksheet(sheet_name)
        columns = list(old_df.columns)

        old_keyed = old_df.set_index(old_df[key_column].astype(str), drop=False)
        new_keyed = new_df.set_index(new_df[key_column].astype(str), drop=False)

        old_keys = set(old_keyed.index)
        new_keys = set(new_keyed.index)

        common_keys = old_keys & new_keys
        added_keys = new_keys - old_keys
        removed_keys = old_keys - new_keys

        # Map each key to its ORIGINAL sheet row number (based on old_df order)
        key_to_sheet_row = {
            str(key): idx + 2 for idx, key in enumerate(old_df[key_column])
        }

        # 1. Updates: same key, changed cells
        cell_updates = []
        for key in common_keys:
            sheet_row = key_to_sheet_row[key]
            old_row = old_keyed.loc[key]
            new_row = new_keyed.loc[key]

            for col_idx, column in enumerate(columns):
                old_value = old_row[column]
                new_value = new_row[column]

                old_empty = pd.isna(old_value) or old_value == ""
                new_empty = pd.isna(new_value) or new_value == ""

                if old_empty and new_empty:
                    continue
                if str(old_value) == str(new_value):
                    continue

                cell_updates.append({
                    "range": gspread.utils.rowcol_to_a1(sheet_row, col_idx + 1),
                    "values": [["" if new_empty else str(new_value)]],
                })

        if cell_updates:
            worksheet.batch_update(cell_updates)
            print(f"Updated {len(cell_updates)} changed cells in sheet: {sheet_name}")

        # 2. Appends: keys only in new_df
        if added_keys:
            new_rows_df = new_keyed.loc[list(added_keys), columns]
            rows_to_append = new_rows_df.fillna("").astype(str).values.tolist()
            worksheet.append_rows(rows_to_append)
            print(f"Appended {len(rows_to_append)} new rows to sheet: {sheet_name}")

        # 3. Deletions: keys only in old_df
        if removed_keys:
            rows_to_delete = sorted(
                (key_to_sheet_row[key] for key in removed_keys), reverse=True
            )
            for row_num in rows_to_delete:
                worksheet.delete_rows(row_num)
            print(f"Deleted {len(rows_to_delete)} rows from sheet: {sheet_name}")