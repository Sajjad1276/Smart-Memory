from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import SavedItemModel, SearchTokenModel


class SavedItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: UUID,
        event_key: bytes,
        storage_message_id: int,
        content_type: str,
        source_type: str,
        token_hashes: Sequence[bytes],
        saved_at: datetime,
    ) -> UUID:
        item = SavedItemModel(
            user_id=user_id,
            event_key=event_key,
            storage_message_id=storage_message_id,
            content_type=content_type,
            source_type=source_type,
            saved_at=saved_at,
        )
        self._session.add(item)
        await self._session.flush()

        self._session.add_all(
            [
                SearchTokenModel(item_id=item.id, token_hash=token_hash)
                for token_hash in set(token_hashes)
            ]
        )
        return item.id

    async def get_by_event_key(self, event_key: bytes) -> SavedItemModel | None:
        result = await self._session.execute(
            select(SavedItemModel).where(SavedItemModel.event_key == event_key)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        *,
        user_id: UUID,
        token_hashes: Sequence[bytes],
        limit: int = 10,
    ) -> list[SavedItemModel]:
        hashes = list(set(token_hashes))
        if not hashes:
            return []

        stmt = (
            select(SavedItemModel)
            .join(SearchTokenModel, SearchTokenModel.item_id == SavedItemModel.id)
            .where(
                SavedItemModel.user_id == user_id,
                SearchTokenModel.token_hash.in_(hashes),
            )
            .group_by(SavedItemModel.id)
            .having(
                func.count(func.distinct(SearchTokenModel.token_hash)) == len(hashes)
            )
            .order_by(SavedItemModel.saved_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars())
