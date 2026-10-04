from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "حافظه هوشمند آماده است.\n\n"
        "برای اتصال فضای ذخیره‌سازی خصوصی: /connect_storage\n"
        "برای جستجو: /search عبارت\n"
        "برای حذف داده‌های مدیریتی: /delete_data\n\n"
        "محتوای اصلی در کانال خصوصی خودت در تلگرام نگهداری می‌شود."
    )
