from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import UserModel
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.security.privacy import PrivacyHasher

router = Router(name="privacy")


@router.message(Command("delete_data"))
async def delete_data(message: Message, session: AsyncSession, hasher: PrivacyHasher) -> None:
    if message.from_user is None:
        return

    user = await UserRepository(session).get_by_user_key(hasher.user_key(message.from_user.id))
    if user is not None:
        await session.execute(delete(UserModel).where(UserModel.id == user.id))
        await session.commit()

    await message.answer(
        "داده‌های مدیریتی این سرویس حذف شد. محتوای کانال خصوصی شما در تلگرام حذف نمی‌شود."
    )
