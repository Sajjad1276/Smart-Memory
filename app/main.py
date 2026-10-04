import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.routers import build_router
from app.config.settings import get_settings
from app.infrastructure.db.session import create_engine, create_session_factory
from app.infrastructure.security.privacy import PrivacyHasher
from app.infrastructure.telegram.dependencies import AppDependencies
from app.infrastructure.telegram.middleware import ServiceMiddleware
from app.infrastructure.telegram.storage import TelegramStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


async def run() -> None:
    settings = get_settings()
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    deps = AppDependencies(
        bot=bot,
        session_factory=session_factory,
        storage=TelegramStorage(bot),
        hasher=PrivacyHasher(bytes.fromhex(settings.privacy_hash_key.get_secret_value())),
    )

    dp = Dispatcher()
    dp.message.middleware(ServiceMiddleware(deps))
    dp.include_router(build_router())

    try:
        await bot.delete_webhook(drop_pending_updates=False)
        await dp.start_polling(bot)
    finally:
        await engine.dispose()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(run())
