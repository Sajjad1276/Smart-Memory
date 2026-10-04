from datetime import datetime, timezone

from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.message_inspector import (
    get_content_type,
    get_searchable_text,
    get_source_type,
)
from app.infrastructure.db.repositories.saved_item_repository import SavedItemRepository
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.security.privacy import PrivacyHasher, tokenize
from app.infrastructure.telegram.storage import TelegramStorage


class StorageNotConfiguredError(ValueError):
    pass


class StorageUnavailableError(ValueError):
    pass


class SaveMessageService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        storage: TelegramStorage,
        hasher: PrivacyHasher,
    ) -> None:
        self._session = session
        self._storage = storage
        self._hasher = hasher

    async def execute(self, message: Message) -> int:
        if message.from_user is None:
            raise ValueError("Message sender is unavailable")

        user_key = self._hasher.user_key(message.from_user.id)
        user_repo = UserRepository(self._session)
        item_repo = SavedItemRepository(self._session)
        user = await user_repo.get_or_create(user_key)

        if user.storage_chat_id is None:
            raise StorageNotConfiguredError("Storage is not configured")

        event_key = self._hasher.event_key(
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            message_id=message.message_id,
        )
        existing = await item_repo.get_by_event_key(event_key)
        if existing is not None:
            return existing.storage_message_id

        try:
            storage_message_id = await self._storage.copy_in(message, user.storage_chat_id)
        except TelegramAPIError as exc:
            await self._session.rollback()
            raise StorageUnavailableError("Telegram storage is unavailable") from exc

        token_hashes = self._hasher.token_keys(
            user_key,
            tokenize(get_searchable_text(message)),
        )
        await item_repo.create(
            user_id=user.id,
            event_key=event_key,
            storage_chat_id=user.storage_chat_id,
            storage_message_id=storage_message_id,
            content_type=get_content_type(message).value,
            source_type=get_source_type(message).value,
            token_hashes=token_hashes,
            saved_at=datetime.now(timezone.utc),
        )
        await self._session.commit()
        return storage_message_id
