from datetime import date, timedelta

import pandas as pd

from src.config.sheets import ReminderColumn, SubscriptionColumn, ReminderConfigColumn
from src.models.remainder import ReminderStatus


class ReminderService:

    @staticmethod
    def get_enabled_configs(reminder_config_df: pd.DataFrame,) -> pd.DataFrame:
        return reminder_config_df[reminder_config_df[ReminderConfigColumn.ENABLED].astype(str).str.upper().eq("TRUE")]

    @staticmethod
    def get_next_reminder_id(reminders_df: pd.DataFrame,) -> int:
        if reminders_df.empty: return 1
        ids = pd.to_numeric(reminders_df[ReminderColumn.ID], errors="coerce",).dropna()
        if ids.empty: return 1
        return int(ids.max()) + 1

    @staticmethod
    def reminder_exists(
        reminders_df: pd.DataFrame,
        subscription_id: int,
        reminder_days: int,
    ) -> bool:

        if reminders_df.empty: return False

        return (
            (reminders_df[ReminderColumn.SUBSCRIPTION_ID].astype(str) == str(subscription_id))
            & (reminders_df[ReminderColumn.REMINDER_DAYS].astype(str) == str(reminder_days))
        ).any()

    @staticmethod
    def build_reminder(reminder_id: int, subscription_id: int,
        reminder_days: int, scheduled_date: date,) -> dict:
        return {
            ReminderColumn.ID: reminder_id,
            ReminderColumn.SUBSCRIPTION_ID: subscription_id,
            ReminderColumn.REMINDER_DAYS: reminder_days,
            ReminderColumn.SCHEDULED_DATE: scheduled_date,
            ReminderColumn.SENT_AT: "",
            ReminderColumn.STATUS: ReminderStatus.PENDING,
            ReminderColumn.ERROR: "",
        }

    @classmethod
    def process_subscription(
        cls,
        subscription: pd.Series,
        enabled_configs: pd.DataFrame,
        reminders_df: pd.DataFrame,
        next_reminder_id: int,
    ) -> tuple[list[dict], int]:

        if not subscription[SubscriptionColumn.STATUS] == "active":
            return [], next_reminder_id

        subscription_id = int(subscription[SubscriptionColumn.ID])
        expiry_date = pd.to_datetime(subscription[SubscriptionColumn.EXPIRY_DATE]).date()

        new_reminders = []
        for _, config in enabled_configs.iterrows():
            reminder_days = int(config[ReminderColumn.REMINDER_DAYS])

            if cls.reminder_exists(
                reminders_df=reminders_df,
                subscription_id=subscription_id,
                reminder_days=reminder_days,
            ): continue

            reminder = cls.build_reminder(
                reminder_id=next_reminder_id,
                subscription_id=subscription_id,
                reminder_days=reminder_days,
                scheduled_date=(expiry_date - timedelta(days=reminder_days)),
            )

            new_reminders.append(reminder)
            next_reminder_id += 1
        return (new_reminders, next_reminder_id,)

    @classmethod
    def create_reminders(cls, subscriptions_df: pd.DataFrame,
        reminders_df: pd.DataFrame, reminder_config_df: pd.DataFrame,
    ) -> pd.DataFrame:
        enabled_configs = cls.get_enabled_configs(reminder_config_df)
        if enabled_configs.empty: return cls.build_result([])
        next_reminder_id = (cls.get_next_reminder_id(reminders_df))
        new_reminders = []
        for _, subscription in subscriptions_df.iterrows():
            try:
                reminders, next_reminder_id = (
                    cls.process_subscription(
                        subscription=subscription, enabled_configs=enabled_configs,
                        reminders_df=reminders_df, next_reminder_id=next_reminder_id,)
                )
                new_reminders.extend(reminders)
            except Exception as error:
                subscription_id = subscription.get(SubscriptionColumn.ID, "unknown")
                print(
                    f"Failed to process "
                    f"subscription "
                    f"{subscription_id}: "
                    f"{error}"
                )
        return pd.DataFrame(new_reminders)
    