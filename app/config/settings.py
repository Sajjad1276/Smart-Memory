from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    bot_token: SecretStr = Field(alias="BOT_TOKEN")
    database_url: str = Field(alias="DATABASE_URL")
    privacy_hash_key: SecretStr = Field(alias="PRIVACY_HASH_KEY")

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return "postgresql+asyncpg://" + value[len("postgresql://") :]
        return value

    @field_validator("privacy_hash_key")
    @classmethod
    def validate_privacy_key(cls, value: SecretStr) -> SecretStr:
        raw = value.get_secret_value()
        if len(raw) != 64:
            raise ValueError("PRIVACY_HASH_KEY must be exactly 64 hexadecimal characters")
        try:
            bytes.fromhex(raw)
        except ValueError as exc:
            raise ValueError("PRIVACY_HASH_KEY must be hexadecimal") from exc
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
