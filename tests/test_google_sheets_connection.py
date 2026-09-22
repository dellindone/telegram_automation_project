from src.clients.google_sheets import GoogleSheetsClient
from src.config.sheets import SheetName


def test_google_sheets_connection():
    client = GoogleSheetsClient()
    df = client.get_sheet_as_dataframe(SheetName.MEMBERS)

    assert df is not None
    print(f"\nGoogle Sheets connected successfully.")
    print(f"Members rows: {len(df)}")
    print(df.head())
    