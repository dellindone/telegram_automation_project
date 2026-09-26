import asyncio
from src.clients.google_sheets import GoogleSheetsClient
from src.clients.telegram import TelegramClient
from src.config.sheets import SheetName, MemberColumn
from src.services.update_members import MembersUpdater

async def update_members(sheets: GoogleSheetsClient, telegram: TelegramClient):
    members_df = sheets.get_sheet_as_dataframe(SheetName.MEMBERS)
    new_members_df = await MembersUpdater.update_members(members_df, telegram)
    sheets.sync_dataframe_to_sheet(
        sheet_name=SheetName.MEMBERS,
        old_df=members_df,
        new_df=new_members_df,
        key_column=MemberColumn.TELEGRAM_USER_ID
    )

async def main():
    print()
    sheets = GoogleSheetsClient()
    telegram = TelegramClient()
    await telegram.connect()
    await update_members(sheets, telegram)
    await telegram.disconnect()
    print("members update process completed.")

if __name__ == "__main__":
    asyncio.run(main())
