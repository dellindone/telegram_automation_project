from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_credentials_file: str
    google_sheet_id: str

    telegram_bot_token: str
    telegram_group_id: int

    telegram_api_id: int
    telegram_api_hash: str
    telegram_phone: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
