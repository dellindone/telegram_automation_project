import asyncio

from src.clients.google_sheets import GoogleSheetsClient
from src.config.sheets import SheetName
from src.services.expired_user_removal import ExpiredUserRemovalService
from src.clients.telegram import TelegramClient

async def remove_expired_users(sheets: GoogleSheetsClient, telegram: TelegramClient,) -> None:
    print()
    subscriptions_df = sheets.get_sheet_as_dataframe(SheetName.SUBSCRIPTIONS)
    members_df = sheets.get_sheet_as_dataframe(SheetName.MEMBERS)
    reminder_config_df = sheets.get_sheet_as_dataframe(SheetName.REMINDER_CONFIG)

    updated_subscriptions_df, updated_members_df = (
        await ExpiredUserRemovalService.remove_expired_users(
            subscriptions_df=subscriptions_df,
            members_df=members_df,
            reminder_config_df=reminder_config_df,
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

async def main():
    sheets = GoogleSheetsClient()
    telegram = TelegramClient()
    await telegram.connect()
    await remove_expired_users(sheets, telegram)
    await telegram.disconnect()
    print("Expired user removal process completed.")

if __name__ == "__main__":
    asyncio.run(main())
