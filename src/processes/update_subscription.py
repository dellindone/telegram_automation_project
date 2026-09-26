
from src.clients.google_sheets import GoogleSheetsClient
from src.config.sheets import SheetName, SubscriptionColumn
from src.services.subscription import SubscriptionService

def update_subscriptions(sheets: GoogleSheetsClient):
    subscriptions_df = sheets.get_sheet_as_dataframe(SheetName.SUBSCRIPTIONS)
    updated_df = SubscriptionService.prepare_subscriptions(subscriptions_df)

    sheets.sync_dataframe_to_sheet(
        sheet_name=SheetName.SUBSCRIPTIONS,
        old_df=subscriptions_df,
        new_df=updated_df,
        key_column=SubscriptionColumn.ID
    )

def main():
    print()
    sheets = GoogleSheetsClient()
    update_subscriptions(sheets)
    print("Subscription update process completed.")

if __name__ == "__main__":
    main()
    