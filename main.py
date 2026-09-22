import asyncio

from src.processes.create_remainders import main as create_reminders
from src.processes.send_remainder import main as send_reminders
from src.processes.update_subscription import main as update_subscriptions
from src.processes.remove_expiry import main as remove_expired_users

def main():
    update_subscriptions()
    create_reminders()

async def main_async():
    await send_reminders()
    await remove_expired_users()

if __name__ == "__main__":
    main()
    asyncio.run(main_async())
