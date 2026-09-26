import asyncio

from telethon import TelegramClient as TelethonClient
from telethon.errors import FloodWaitError

from src.config.settings import settings
from src.config.sheets import MemberColumn

class TelegramClient:

    def __init__(self):
        self.client = TelethonClient(
            "telegram_session",
            settings.telegram_api_id,
            settings.telegram_api_hash,
        )
        self.group_id = settings.telegram_group_id

    async def connect(self) -> None:
        if not self.client.is_connected():
            await self.client.start()

    async def disconnect(self) -> None:
        if self.client.is_connected():
            await self.client.disconnect()

    async def ensure_connected(self) -> None:
        if not self.client.is_connected():
            await self.client.connect()

    async def send_message(self, telegram_user_id: int, message: str) -> None:
        await self.ensure_connected()
        await asyncio.sleep(0.4)

        try:
            await self.client.send_message(telegram_user_id, message)
        except FloodWaitError as error:
            print(f"Telegram FloodWait: {error.seconds}s")
            await asyncio.sleep(error.seconds)
            await self.client.send_message(telegram_user_id, message)

    async def remove_user(self, telegram_user_id: int) -> None:
        await self.ensure_connected()
        group = await self.client.get_entity(self.group_id)
        user = await self.client.get_entity(telegram_user_id)
        await self.client.kick_participant(group, user)

    async def get_group_participants(self) -> list:
        await self.ensure_connected()
        group = await self.client.get_entity(self.group_id)
        participants = await self.client.get_participants(group)
        members = []
        for user in participants:
            first_name = user.first_name or ""
            last_name = user.last_name or ""

            members.append({
                    MemberColumn.TELEGRAM_USER_ID: user.id,
                    MemberColumn.USERNAME: user.username or "",
                    MemberColumn.NAME: f"{first_name} {last_name}".strip(),
                })
        return members
    