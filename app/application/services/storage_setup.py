from aiogram import Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.security.privacy import PrivacyHasher
from app.infrastructure.telegram.storage import TelegramStorage


class StorageSetupError(ValueError):
    pass


class StorageSetupService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        bot: Bot,
        storage: TelegramStorage,
        hasher: PrivacyHasher,
    ) -> None:
        self._session = session
        self._bot = bot
        self._storage = storage
        self._hasher = hasher

    async def begin(self, message: Message) -> None:
        if message.from_user is None:
            raise StorageSetupError("Message sender is unavailable")

        user = await UserRepository(self._session).get_or_create(
            self._hasher.user_key(message.from_user.id)
        )
        user.storage_setup_pending = True
        await self._session.commit()

    async def disconnect(self, message: Message) -> bool:
        if message.from_user is None:
            raise StorageSetupError("Message sender is unavailable")

        user = await UserRepository(self._session).get_by_user_key(
            self._hasher.user_key(message.from_user.id)
        )
        if user is None:
            return False

        user.storage_chat_id = None
        user.storage_setup_pending = False
        await self._session.commit()
        return True

    async def connect_from_forward(self, message: Message) -> bool:
        if message.from_user is None or message.forward_origin is None:
            return False

        origin_chat = getattr(message.forward_origin, "chat", None)
        if origin_chat is None or getattr(origin_chat, "type", None) != "channel":
            return False

        user_repo = UserRepository(self._session)
        user = await user_repo.get_or_create(
            self._hasher.user_key(message.from_user.id)
        )
        if not user.storage_setup_pending:
            return False

        storage_chat_id = origin_chat.id
        if not await self._storage.verify_private_channel(storage_chat_id):
            raise StorageSetupError("فضای ذخیره‌سازی باید یک کانال خصوصی باشد.")

        bot_id = (await self._bot.get_me()).id
        if not await self._storage.verify_storage_admin(
            storage_chat_id=storage_chat_id,
            bot_user_id=bot_id,
        ):
            raise StorageSetupError("ربات باید در کانال ذخیره‌سازی ادمین باشد.")

        if not await self._storage.verify_user_admin(
            storage_chat_id=storage_chat_id,
            user_id=message.from_user.id,
        ):
            raise StorageSetupError("شما باید در کانال ذخیره‌سازی ادمین باشید.")

        await user_repo.set_storage_chat(user, storage_chat_id)
        await self._session.commit()
        return True
