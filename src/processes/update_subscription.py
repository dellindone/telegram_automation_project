
from src.clients.google_sheets import GoogleSheetsClient
from src.config.sheets import SheetName
from src.services.subscription import SubscriptionService

def update_subscriptions(sheets: GoogleSheetsClient):
    print()
    subscriptions_df = sheets.get_sheet_as_dataframe(SheetName.SUBSCRIPTIONS)
    updated_df = SubscriptionService.prepare_subscriptions(subscriptions_df)

    sheets.update_changed_rows(
        sheet_name=SheetName.SUBSCRIPTIONS,
        old_df=subscriptions_df,
        new_df=updated_df,
    )

def main():
    sheets = GoogleSheetsClient()
    update_subscriptions(sheets)
    print("Subscription update process completed.")

if __name__ == "__main__":
    main()
    