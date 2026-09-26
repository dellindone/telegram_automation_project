import pandas as pd

from src.clients.telegram import TelegramClient
from src.config.sheets import MemberColumn


class MembersUpdater:
    """Syncs a members DataFrame against the current Telegram group participants."""

    @staticmethod
    def _normalize_telegram_ids(members_df: pd.DataFrame, new_members_df: pd.DataFrame,) -> tuple[pd.DataFrame, pd.DataFrame]:
        column = MemberColumn.TELEGRAM_USER_ID
        members_df[column] = members_df[column].astype(str).str.strip()
        new_members_df[column] = new_members_df[column].astype(str).str.strip()
        new_members_df = new_members_df.drop_duplicates(subset=[column], keep="last")
        return members_df, new_members_df

    @staticmethod
    def _merge_members(members_df: pd.DataFrame, new_members_df: pd.DataFrame,
    ) -> pd.DataFrame:
        columns = [
            MemberColumn.TELEGRAM_USER_ID,
            MemberColumn.USERNAME,
            MemberColumn.NAME,
        ]

        return members_df.merge(
            new_members_df[columns],
            on=MemberColumn.TELEGRAM_USER_ID,
            how="outer",
            suffixes=("", "_telegram"),
            indicator=True,
        )

    @staticmethod
    def _update_existing_members(merged: pd.DataFrame) -> pd.DataFrame:
        username = MemberColumn.USERNAME
        name = MemberColumn.NAME
        status = MemberColumn.STATUS

        existing_member = merged["_merge"] == "both"

        # Pull fresh data from Telegram, falling back to existing value if missing
        merged.loc[existing_member, username] = (
            merged.loc[existing_member, f"{username}_telegram"]
            .fillna(merged.loc[existing_member, username])
        )
        merged.loc[existing_member, name] = (
            merged.loc[existing_member, f"{name}_telegram"]
            .fillna(merged.loc[existing_member, name])
        )

        inactive_reactivated = (
            existing_member
            & merged[status].fillna("").str.lower().eq("inactive")
        )
        merged.loc[inactive_reactivated, status] = "new"
        return merged

    @staticmethod
    def _add_new_members(merged: pd.DataFrame) -> pd.DataFrame:
        member_id = MemberColumn.ID
        status = MemberColumn.STATUS
        joined_date = MemberColumn.JOINED_DATE

        new_member_mask = merged["_merge"] == "right_only"
        new_count = new_member_mask.sum()

        if new_count == 0: return merged

        existing_ids = pd.to_numeric(merged.loc[~new_member_mask, member_id], errors="coerce")
        max_id = existing_ids.max()
        max_id = 0 if pd.isna(max_id) else int(max_id)

        merged.loc[new_member_mask, member_id] = range(max_id + 1, max_id + 1 + new_count)
        merged.loc[new_member_mask, status] = "new"
        merged.loc[new_member_mask, joined_date] = pd.Timestamp.now().strftime("%Y-%m-%d")
        return merged

    @staticmethod
    def _cleanup_members(merged: pd.DataFrame, original_columns: pd.Index,) -> pd.DataFrame:
        username = MemberColumn.USERNAME
        name = MemberColumn.NAME

        merged[username] = merged[username].fillna(merged[f"{username}_telegram"]).fillna("")
        merged[name] = merged[name].fillna(merged[f"{name}_telegram"]).fillna("")

        merged = merged.drop(
            columns=[
                f"{username}_telegram",
                f"{name}_telegram",
                "_merge",
            ],
            errors="ignore",
        )
        return merged[original_columns]

    @staticmethod
    async def update_members(members_df: pd.DataFrame, telegram: TelegramClient,) -> pd.DataFrame:
        members = await telegram.get_group_participants()

        if not members:
            print("No Telegram members found.")
            return members_df

        new_members_df = pd.DataFrame(members)
        original_columns = members_df.columns

        members_df, new_members_df = MembersUpdater._normalize_telegram_ids(members_df, new_members_df,)
        merged = MembersUpdater._merge_members(members_df, new_members_df)
        merged = MembersUpdater._update_existing_members(merged)
        merged = MembersUpdater._add_new_members(merged)
        return MembersUpdater._cleanup_members(merged, original_columns)
    