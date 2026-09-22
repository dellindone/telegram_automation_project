import asyncio

from src.clients.google_sheets import GoogleSheetsClient
from src.config.sheets import SheetName
from src.services.expired_user_removal import ExpiredUserRemovalService
from src.clients.telegram import TelegramClient

async def remove_expired_users(sheets: GoogleSheetsClient, telegram: TelegramClient,) -> None:
    print()
    subscriptions_df = sheets.get_sheet_as_dataframe(SheetName.SUBSCRIPTIONS)
    members_df = sheets.get_sheet_as_dataframe(SheetName.MEMBERS)
    reminders_df = sheets.get_sheet_as_dataframe(SheetName.REMINDERS)

    updated_subscriptions_df, updated_members_df, updated_reminders_df = (
        await ExpiredUserRemovalService.remove_expired_users(
            subscriptions_df=subscriptions_df,
            members_df=members_df,
            reminders_df=reminders_df,
            telegram=telegram,
        )
    )

    sheets.update_changed_rows(
        sheet_name=SheetName.SUBSCRIPTIONS,
        old_df=subscriptions_df,
        new_df=updated_subscriptions_df,
    )

    sheets.update_changed_rows(
        sheet_name=SheetName.MEMBERS,
        old_df=members_df,
        new_df=updated_members_df,
    )

    sheets.update_changed_rows(
        sheet_name=SheetName.REMINDERS,
        old_df=reminders_df,
        new_df=updated_reminders_df,
    )

async def main():
    sheets = GoogleSheetsClient()
    telegram = TelegramClient()
    await remove_expired_users(sheets, telegram)

if __name__ == "__main__":
    asyncio.run(main())
