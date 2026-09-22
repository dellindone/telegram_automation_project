from src.clients.google_sheets import GoogleSheetsClient
from src.services.remainder import ReminderService
from src.config.sheets import SheetName

def create_reminders(sheets: GoogleSheetsClient) -> None:
    print()
    subscriptions_df = sheets.get_sheet_as_dataframe(SheetName.SUBSCRIPTIONS)
    reminders_df = sheets.get_sheet_as_dataframe(SheetName.REMINDERS)
    reminder_config_df = sheets.get_sheet_as_dataframe(SheetName.REMINDER_CONFIG)

    new_reminders_df = ReminderService.create_reminders(
        subscriptions_df=subscriptions_df,
        reminders_df=reminders_df,
        reminder_config_df=reminder_config_df,
    )

    if new_reminders_df.empty:
        print("No new reminders to create.")
        return
    sheets.append_rows(sheet_name=SheetName.REMINDERS, df=new_reminders_df)

def main():
    sheets = GoogleSheetsClient()
    create_reminders(sheets)
    print("Reminder creation process completed.")

if __name__ == "__main__":
    main()
    