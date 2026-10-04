from dataclasses import dataclass

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.infrastructure.security.privacy import PrivacyHasher
from app.infrastructure.telegram.storage import TelegramStorage


@dataclass(frozen=True, slots=True)
class AppDependencies:
    bot: Bot
    session_factory: async_sessionmaker
    storage: TelegramStorage
    hasher: PrivacyHasher
