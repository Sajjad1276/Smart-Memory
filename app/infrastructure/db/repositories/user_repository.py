from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_key(self, user_key: bytes) -> UserModel | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.user_key == user_key)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_key: bytes) -> UserModel:
        existing = await self.get_by_user_key(user_key)
        if existing is not None:
            return existing

        stmt = (
            insert(UserModel)
            .values(user_key=user_key)
            .on_conflict_do_nothing(index_elements=[UserModel.user_key])
        )
        await self._session.execute(stmt)
        result = await self._session.execute(
            select(UserModel).where(UserModel.user_key == user_key)
        )
        return result.scalar_one()

    async def set_storage_chat(self, user: UserModel, storage_chat_id: int) -> None:
        user.storage_chat_id = storage_chat_id
        user.storage_setup_pending = False
        await self._session.flush()
