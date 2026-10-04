from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.save_message import (
    StorageNotConfiguredError,
    StorageUnavailableError,
)
from app.infrastructure.db.repositories.saved_item_repository import SavedItemRepository
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.security.privacy import PrivacyHasher, tokenize
from app.infrastructure.telegram.storage import TelegramStorage


class SearchMemoryService:
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

    async def execute(self, message: Message, query: str, limit: int = 10) -> int:
        if message.from_user is None:
            raise ValueError("Message sender is unavailable")

        query = query.strip()
        if not query or len(query) > 512:
            return 0

        user_key = self._hasher.user_key(message.from_user.id)
        user_repo = UserRepository(self._session)
        item_repo = SavedItemRepository(self._session)
        user = await user_repo.get_by_user_key(user_key)
        if user is None or user.storage_chat_id is None:
            raise StorageNotConfiguredError("Storage is not configured")

        hashes = self._hasher.token_keys(user_key, tokenize(query))
        items = await item_repo.search(
            user_id=user.id,
            token_hashes=hashes,
            limit=max(1, min(limit, 20)),
        )

        try:
            for item in items:
                await self._storage.copy_out(
                    target_chat_id=message.chat.id,
                    storage_chat_id=user.storage_chat_id,
                    storage_message_id=item.storage_message_id,
                )
        except TelegramAPIError as exc:
            raise StorageUnavailableError("Telegram storage is unavailable") from exc

        return len(items)
