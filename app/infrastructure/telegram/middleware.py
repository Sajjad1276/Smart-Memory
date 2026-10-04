from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.save_message import SaveMessageService
from app.application.services.search_memory import SearchMemoryService
from app.application.services.storage_setup import StorageSetupService
from app.infrastructure.telegram.dependencies import AppDependencies


class ServiceMiddleware(BaseMiddleware):
    def __init__(self, deps: AppDependencies) -> None:
        self._deps = deps

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self._deps.session_factory() as session:
            data["session"] = session
            data["save_service"] = SaveMessageService(
                session=session,
                storage=self._deps.storage,
                hasher=self._deps.hasher,
            )
            data["search_service"] = SearchMemoryService(
                session=session,
                storage=self._deps.storage,
                hasher=self._deps.hasher,
            )
            data["storage_setup"] = StorageSetupService(
                session=session,
                bot=self._deps.bot,
                storage=self._deps.storage,
                hasher=self._deps.hasher,
            )
            data["hasher"] = self._deps.hasher
            return await handler(event, data)
