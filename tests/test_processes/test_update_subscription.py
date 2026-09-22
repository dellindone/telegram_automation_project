from unittest.mock import MagicMock, patch

import pandas as pd

from src.config.sheets import SheetName, SubscriptionColumn


@patch("src.processes.update_subscription.SubscriptionService.prepare_subscriptions")
def test_update_subscriptions(mock_prepare_subscriptions):
    from src.processes.update_subscription import update_subscriptions

    sheets = MagicMock()
    subscriptions_df = pd.DataFrame([{SubscriptionColumn.ID: 1, SubscriptionColumn.STATUS: "active"}])
    updated_df = subscriptions_df.copy()
    mock_prepare_subscriptions.return_value = updated_df
    sheets.get_sheet_as_dataframe.return_value = subscriptions_df

    update_subscriptions(sheets)

    sheets.get_sheet_as_dataframe.assert_called_once_with(SheetName.SUBSCRIPTIONS)
    mock_prepare_subscriptions.assert_called_once_with(subscriptions_df)
    sheets.update_changed_rows.assert_called_once_with(
        sheet_name=SheetName.SUBSCRIPTIONS,
        old_df=subscriptions_df,
        new_df=updated_df,
    )