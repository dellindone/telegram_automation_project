from datetime import date, datetime

import pandas as pd

from src.clients.telegram import TelegramClient
from src.config.sheets import MemberColumn, ReminderColumn, SubscriptionColumn


class ReminderSendingService:

    @staticmethod
    def get_due_reminders(reminders_df: pd.DataFrame) -> pd.DataFrame:
        if reminders_df.empty: return reminders_df

        today = date.today()
        scheduled_dates = pd.to_datetime(reminders_df[ReminderColumn.SCHEDULED_DATE], errors="coerce").dt.date
        return reminders_df[(reminders_df[ReminderColumn.STATUS] == "pending") & (scheduled_dates <= today)]

    @staticmethod
    def build_expiry_message(expiry_date, reminder_days: int) -> str:
        return f"Your Telegram group subscription will expire in {reminder_days} day(s) on {expiry_date}."

    @staticmethod
    def get_telegram_user_id(subscription: pd.Series, members_df: pd.DataFrame) -> int:
        member_id = subscription[SubscriptionColumn.MEMBER_ID]
        member = members_df[members_df[MemberColumn.ID] == member_id]

        if member.empty: raise ValueError(f"Member {member_id} not found.")
        return int(member.iloc[0][MemberColumn.TELEGRAM_USER_ID])

    @classmethod
    async def send_due_reminders(
        cls, reminders_df: pd.DataFrame,
        subscriptions_df: pd.DataFrame, members_df: pd.DataFrame,
        telegram: TelegramClient,
    ) -> pd.DataFrame:
        result_df = reminders_df.copy()
        due_reminders = cls.get_due_reminders(result_df)

        for index, reminder in due_reminders.iterrows():
            try:
                subscription = subscriptions_df[subscriptions_df[SubscriptionColumn.ID] == reminder[ReminderColumn.SUBSCRIPTION_ID]]
                if subscription.empty: raise ValueError("Subscription not found.")
                subscription = subscription.iloc[0]
                telegram_user_id = cls.get_telegram_user_id(subscription, members_df)

                message = cls.build_expiry_message(
                    expiry_date=subscription[SubscriptionColumn.EXPIRY_DATE],
                    reminder_days=int(reminder[ReminderColumn.REMINDER_DAYS]),
                )

                await telegram.send_message(telegram_user_id=telegram_user_id, message=message,)
                result_df.at[index, ReminderColumn.STATUS] = "sent"
                result_df.at[index, ReminderColumn.SENT_AT] = datetime.now()
            except Exception as error:
                result_df.at[index, ReminderColumn.STATUS] = "failed"
                result_df.at[index, ReminderColumn.ERROR] = str(error)

        return result_df
    