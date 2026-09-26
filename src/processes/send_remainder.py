import asyncio

from src.clients.google_sheets import GoogleSheetsClient
from src.clients.telegram import TelegramClient
from src.services.remainder_sending import ReminderSendingService
from src.config.sheets import SheetName, SubscriptionColumn

async def send_reminders(sheets: GoogleSheetsClient, telegram: TelegramClient) -> None:
    reminders_df = sheets.get_sheet_as_dataframe(SheetName.REMINDERS)
    subscriptions_df = sheets.get_sheet_as_dataframe(SheetName.SUBSCRIPTIONS)
    members_df = sheets.get_sheet_as_dataframe(SheetName.MEMBERS)
    config_df = sheets.get_sheet_as_dataframe(SheetName.REMINDER_CONFIG)

    updated_reminders_df = await ReminderSendingService.send_due_reminders(
        reminders_df=reminders_df,
        subscriptions_df=subscriptions_df,
        members_df=members_df,
        config_df=config_df,
        telegram=telegram,
    )

    sheets.sync_dataframe_to_sheet(
        sheet_name=SheetName.REMINDERS,
        old_df=reminders_df,
        new_df=updated_reminders_df,
        key_column=SubscriptionColumn.ID
    )

async def main():
    print()
    sheets = GoogleSheetsClient()
    telegram = TelegramClient()
    await telegram.connect()
    await send_reminders(sheets, telegram)
    await telegram.disconnect()
    print("Reminder sending process completed.")

if __name__ == "__main__":
    asyncio.run(main())
    