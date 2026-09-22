from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.clients.telegram import TelegramClient


@patch("src.clients.telegram.TelethonClient")
def test_telegram_client_initialization(mock_telethon_client):
    client = TelegramClient()

    mock_telethon_client.assert_called_once()
    assert client.group_id is not None


@patch("src.clients.telegram.TelethonClient")
@pytest.mark.asyncio
async def test_send_message(mock_telethon_client):
    telethon_client = MagicMock()
    telethon_client.send_message = AsyncMock()
    mock_telethon_client.return_value = telethon_client

    client = TelegramClient()

    await client.send_message(
        telegram_user_id=1090899134,
        message="Test message",
    )

    telethon_client.send_message.assert_awaited_once_with(
        1090899134,
        "Test message",
    )


@patch("src.clients.telegram.TelethonClient")
@pytest.mark.asyncio
async def test_remove_user(mock_telethon_client):
    telethon_client = MagicMock()
    telethon_client.get_entity = AsyncMock(side_effect=["group", "user"])
    telethon_client.kick_participant = AsyncMock()
    mock_telethon_client.return_value = telethon_client

    client = TelegramClient()

    await client.remove_user(1090899134)

    assert telethon_client.get_entity.await_count == 2
    telethon_client.kick_participant.assert_awaited_once_with(
        "group",
        "user",
    )


@patch("src.clients.telegram.TelethonClient")
@pytest.mark.asyncio
async def test_remove_user_failure(mock_telethon_client):
    telethon_client = MagicMock()
    telethon_client.get_entity = AsyncMock(side_effect=RuntimeError("User not found"))
    mock_telethon_client.return_value = telethon_client

    client = TelegramClient()

    with pytest.raises(RuntimeError, match="User not found"):
        await client.remove_user(1090899134)