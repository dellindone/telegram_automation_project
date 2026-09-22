import gc
from datetime import datetime, timedelta

import pandas as pd

from src.config.sheets import SubscriptionColumn
from src.models.subscription import SubscriptionStatus


class SubscriptionService:

    @staticmethod
    def append_error(df: pd.DataFrame, index, error: Exception,) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = (
            f"{timestamp} | "
            f"{type(error).__name__}: {error}"
        )
        error_column = SubscriptionColumn.ERROR

        if error_column not in df.columns: df[error_column] = ""
        existing_error = df.at[index,error_column,]

        if (pd.isna(existing_error) or existing_error == ""):
            df.at[index, error_column,] = error_message
        else:
            df.at[index, error_column,] = (f"{existing_error}\n"f"{error_message}")

    @staticmethod
    def process_row(row: pd.Series,) -> dict:
        subscribe_date = pd.to_datetime(row[SubscriptionColumn.SUBSCRIBE_DATE]).date()
        expired_after = int(row[SubscriptionColumn.EXPIRED_AFTER])
        expiry_date = (subscribe_date + timedelta(days=expired_after))
        status = row[SubscriptionColumn.STATUS]
        if (pd.isna(status) or status == ""): status = SubscriptionStatus.ACTIVE
        created_at = row[SubscriptionColumn.CREATED_AT]
        if (pd.isna(created_at) or created_at == ""): created_at = datetime.now()
        return {
            SubscriptionColumn.SUBSCRIBE_DATE: subscribe_date,
            SubscriptionColumn.EXPIRY_DATE: expiry_date,
            SubscriptionColumn.STATUS: status,
            SubscriptionColumn.CREATED_AT: created_at,
        }

    @classmethod
    def prepare_subscriptions(cls, df: pd.DataFrame,) -> pd.DataFrame:
        result_df = df.copy()
        for index, row in result_df.iterrows():
            try:
                result = cls.process_row(row)
                row_changed = False
                for column, new_value in result.items():
                    old_value = result_df.at[index, column,]

                    if (pd.isna(old_value) and pd.isna(new_value)): continue
                    if str(old_value) != str(new_value):

                        result_df.at[index, column,] = new_value
                        row_changed = True
                    del old_value, new_value

                if row_changed:
                    result_df.at[index, SubscriptionColumn.UPDATED_AT,] = datetime.now()
                del result
                gc.collect()
            except Exception as error:
                cls.append_error(df=result_df, index=index, error=error,)
        return result_df
    