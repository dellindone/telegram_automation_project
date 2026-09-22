
from datetime import date, datetime

import pandas as pd

from src.clients.telegram import TelegramClient
from src.models.member import MemberStatus
from src.config.sheets import MemberColumn, ReminderColumn, SubscriptionColumn


class ExpiredUserRemovalService:

    @staticmethod
    def mark_member_inactive(members_df: pd.DataFrame, member_id: int) -> None:
        member_index = members_df[members_df[MemberColumn.ID] == member_id].index
        if member_index.empty:
            raise ValueError(f"Member {member_id} not found.")
        members_df.loc[member_index[0], MemberColumn.STATUS] = MemberStatus.INACTIVE

    @staticmethod
    def get_expired_subscriptions(subscriptions_df: pd.DataFrame) -> pd.DataFrame:
        if subscriptions_df.empty:
            return subscriptions_df

        today = date.today()
        expiry_dates = pd.to_datetime(
            subscriptions_df[SubscriptionColumn.EXPIRY_DATE],
            errors="coerce",
        ).dt.date

        return subscriptions_df[
            (subscriptions_df[SubscriptionColumn.STATUS] == "active")
            & (expiry_dates <= today)
        ]

    @staticmethod
    def get_telegram_user_id(
        subscription: pd.Series,
        members_df: pd.DataFrame,
    ) -> int:
        member_id = subscription[SubscriptionColumn.MEMBER_ID]
        member = members_df[members_df[MemberColumn.ID] == member_id]

        if member.empty:
            raise ValueError(f"Member {member_id} not found.")

        return int(member.iloc[0][MemberColumn.TELEGRAM_USER_ID])

    @staticmethod
    def mark_removal_pending(df: pd.DataFrame, index) -> None:
        df.at[index, SubscriptionColumn.STATUS] = "removal_pending"
        df.at[index, SubscriptionColumn.UPDATED_AT] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def mark_removed(df: pd.DataFrame, index) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df.at[index, SubscriptionColumn.STATUS] = "removed"
        df.at[index, SubscriptionColumn.REMOVED_AT] = timestamp
        df.at[index, SubscriptionColumn.UPDATED_AT] = timestamp

    @staticmethod
    def mark_removal_failed(
        df: pd.DataFrame,
        index,
        error: Exception,
    ) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"{timestamp} | {type(error).__name__}: {error}"

        error_column = SubscriptionColumn.ERROR
        existing_error = df.at[index, error_column]

        if pd.isna(existing_error) or existing_error == "":
            df.at[index, error_column] = error_message
        else:
            df.at[index, error_column] = f"{existing_error}\n{error_message}"

        df.at[index, SubscriptionColumn.STATUS] = "removal_failed"
        df.at[index, SubscriptionColumn.UPDATED_AT] = timestamp

    @staticmethod
    def remove_reminders(
        reminders_df: pd.DataFrame,
        subscription_id: int,
    ) -> pd.DataFrame:
        return reminders_df[
            reminders_df[ReminderColumn.SUBSCRIPTION_ID] != subscription_id
        ].copy()

    @classmethod
    async def remove_expired_users(
        cls,
        subscriptions_df: pd.DataFrame,
        members_df: pd.DataFrame,
        reminders_df: pd.DataFrame,
        telegram: TelegramClient,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

        result_subscriptions = subscriptions_df.copy()
        result_members = members_df.copy()
        result_reminders = reminders_df.copy()

        expired_subscriptions = cls.get_expired_subscriptions(
            result_subscriptions
        )

        for index, subscription in expired_subscriptions.iterrows():
            try:
                cls.mark_removal_pending(result_subscriptions, index)

                telegram_user_id = cls.get_telegram_user_id(
                    subscription,
                    result_members,
                )

                await telegram.remove_user(telegram_user_id)
                cls.mark_removed(result_subscriptions, index)
                cls.mark_member_inactive(result_members, subscription[SubscriptionColumn.MEMBER_ID],)

                result_reminders = cls.remove_reminders(result_reminders,int(subscription[SubscriptionColumn.ID]),)

            except Exception as error:
                cls.mark_removal_failed(
                    result_subscriptions,
                    index,
                    error,
                )

        return (
            result_subscriptions,
            result_members,
            result_reminders,
        )
