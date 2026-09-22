import pandas as pd

from ...src.config.sheets import SubscriptionColumn
from ...src.models.subscription import SubscriptionStatus
from ...src.services.subscription import SubscriptionService


def test_process_row_calculates_expiry_date():
    row = pd.Series({
        SubscriptionColumn.SUBSCRIBE_DATE: "2026-09-01",
        SubscriptionColumn.EXPIRED_AFTER: 30,
        SubscriptionColumn.STATUS: "",
        SubscriptionColumn.CREATED_AT: "",
    })

    result = SubscriptionService.process_row(row)

    assert result[SubscriptionColumn.EXPIRY_DATE].isoformat() == "2026-10-01"
    assert result[SubscriptionColumn.STATUS] == SubscriptionStatus.ACTIVE
    assert result[SubscriptionColumn.CREATED_AT] is not None


def test_prepare_subscriptions_calculates_expiry_date():
    df = pd.DataFrame([{
        SubscriptionColumn.ID: 1,
        SubscriptionColumn.MEMBER_ID: 10,
        SubscriptionColumn.SUBSCRIBE_DATE: "2026-09-01",
        SubscriptionColumn.EXPIRED_AFTER: 30,
        SubscriptionColumn.EXPIRY_DATE: "",
        SubscriptionColumn.STATUS: "",
        SubscriptionColumn.REMOVED_AT: "",
        SubscriptionColumn.ERROR: "",
        SubscriptionColumn.CREATED_AT: "",
        SubscriptionColumn.UPDATED_AT: "",
    }])

    result = SubscriptionService.prepare_subscriptions(df)

    assert result.loc[0, SubscriptionColumn.EXPIRY_DATE].isoformat() == "2026-10-01"
    assert result.loc[0, SubscriptionColumn.STATUS] == SubscriptionStatus.ACTIVE
    assert result.loc[0, SubscriptionColumn.CREATED_AT] != ""
    assert result.loc[0, SubscriptionColumn.UPDATED_AT] != ""


def test_prepare_subscriptions_keeps_existing_status():
    df = pd.DataFrame([{
        SubscriptionColumn.ID: 1,
        SubscriptionColumn.MEMBER_ID: 10,
        SubscriptionColumn.SUBSCRIBE_DATE: "2026-09-01",
        SubscriptionColumn.EXPIRED_AFTER: 30,
        SubscriptionColumn.EXPIRY_DATE: "",
        SubscriptionColumn.STATUS: "cancelled",
        SubscriptionColumn.REMOVED_AT: "",
        SubscriptionColumn.ERROR: "",
        SubscriptionColumn.CREATED_AT: "",
        SubscriptionColumn.UPDATED_AT: "",
    }])

    result = SubscriptionService.prepare_subscriptions(df)

    assert result.loc[0, SubscriptionColumn.STATUS] == "cancelled"


def test_prepare_subscriptions_records_error_for_invalid_date():
    df = pd.DataFrame([{
        SubscriptionColumn.ID: 1,
        SubscriptionColumn.MEMBER_ID: 10,
        SubscriptionColumn.SUBSCRIBE_DATE: "invalid-date",
        SubscriptionColumn.EXPIRED_AFTER: 30,
        SubscriptionColumn.EXPIRY_DATE: "",
        SubscriptionColumn.STATUS: "",
        SubscriptionColumn.REMOVED_AT: "",
        SubscriptionColumn.ERROR: "",
        SubscriptionColumn.CREATED_AT: "",
        SubscriptionColumn.UPDATED_AT: "",
    }])

    result = SubscriptionService.prepare_subscriptions(df)

    assert result.loc[0, SubscriptionColumn.ERROR] != ""
    assert "DateParseError" in result.loc[0, SubscriptionColumn.ERROR] or "ValueError" in result.loc[0, SubscriptionColumn.ERROR]