from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message

from app.application.services.save_message import (
    SaveMessageService,
    StorageNotConfiguredError,
    StorageUnavailableError,
)

router = Router(name="save")


@router.message()
async def save_message(message: Message, save_service: SaveMessageService) -> None:
    if message.text and message.text.startswith("/"):
        return

    try:
        await save_service.execute(message)
    except StorageNotConfiguredError:
        await message.answer("ابتدا /connect_storage را اجرا کن.")
        return
    except StorageUnavailableError:
        await message.answer("ذخیره‌سازی تلگرام در دسترس نیست. کانال ذخیره‌سازی و دسترسی ربات را بررسی کن.")
        return
    except TelegramAPIError:
        await message.answer("پردازش پیام انجام نشد.")
        return

    await message.answer("ذخیره شد.")
