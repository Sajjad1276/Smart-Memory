from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.application.services.save_message import (
    SaveMessageService,
    StorageNotConfiguredError,
    StorageUnavailableError,
)
from app.application.services.storage_setup import StorageSetupError, StorageSetupService

router = Router(name="storage")


@router.message(Command("connect_storage", "storage"))
async def connect_storage(message: Message, storage_setup: StorageSetupService) -> None:
    try:
        await storage_setup.begin(message)
    except StorageSetupError:
        await message.answer("فعال‌سازی فضای ذخیره‌سازی انجام نشد.")
        return

    await message.answer(
        "یک کانال خصوصی برای حافظه خود بساز. ربات را ادمین کانال کن و سپس یک پست از همان کانال را برای من فوروارد کن."
    )


@router.message(Command("disconnect_storage"))
async def disconnect_storage(message: Message, storage_setup: StorageSetupService) -> None:
    await storage_setup.disconnect(message)
    await message.answer("ارتباط با فضای ذخیره‌سازی حذف شد. محتوای کانال تلگرام شما حذف نمی‌شود.")


@router.message(F.forward_origin)
async def consume_storage_proof(
    message: Message,
    storage_setup: StorageSetupService,
    save_service: SaveMessageService,
) -> None:
    try:
        connected = await storage_setup.connect_from_forward(message)
    except StorageSetupError as exc:
        await message.answer(str(exc))
        return

    if connected:
        await message.answer("فضای ذخیره‌سازی وصل شد. از این بعد هر محتوا را برای من بفرست تا ذخیره شود.")
        return

    try:
        await save_service.execute(message)
    except StorageNotConfiguredError:
        await message.answer("ابتدا /connect_storage را اجرا کن.")
    except StorageUnavailableError:
        await message.answer("ذخیره‌سازی تلگرام در دسترس نیست.")
