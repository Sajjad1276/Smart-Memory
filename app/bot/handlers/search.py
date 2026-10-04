from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.application.services.save_message import StorageNotConfiguredError, StorageUnavailableError
from app.application.services.search_memory import SearchMemoryService

router = Router(name="search")


@router.message(Command("search"))
async def search(message: Message, search_service: SearchMemoryService) -> None:
    if not message.text:
        return

    query = message.text.partition(" ")[2].strip()
    if not query:
        await message.answer("فرمت: /search عبارت")
        return

    try:
        count = await search_service.execute(message, query)
    except StorageNotConfiguredError:
        await message.answer("ابتدا /connect_storage را اجرا کن.")
        return
    except StorageUnavailableError:
        await message.answer("فضای ذخیره‌سازی تلگرام در دسترس نیست.")
        return

    await message.answer(f"{count} نتیجه پیدا شد.")
