import asyncio

from src.clients.google_sheets import GoogleSheetsClient
from src.clients.telegram import TelegramClient
from src.services.remainder_sending import ReminderSendingService
from src.config.sheets import SheetName

async def send_reminders(sheets: GoogleSheetsClient, telegram: TelegramClient) -> None:
    print()
    reminders_df = sheets.get_sheet_as_dataframe(SheetName.REMINDERS)
    subscriptions_df = sheets.get_sheet_as_dataframe(SheetName.SUBSCRIPTIONS)
    members_df = sheets.get_sheet_as_dataframe(SheetName.MEMBERS)

    updated_reminders_df = await ReminderSendingService.send_due_reminders(
        reminders_df=reminders_df,
        subscriptions_df=subscriptions_df,
        members_df=members_df,
        telegram=telegram,
    )

    sheets.update_changed_rows(
        sheet_name=SheetName.REMINDERS,
        old_df=reminders_df,
        new_df=updated_reminders_df,
    )

async def main():
    sheets = GoogleSheetsClient()
    telegram = TelegramClient()
    await telegram.connect()
    await send_reminders(sheets, telegram)
    await telegram.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
    