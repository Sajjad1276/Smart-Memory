from aiogram import Bot
from aiogram.types import Message


class TelegramStorage:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def copy_in(self, message: Message, storage_chat_id: int) -> int:
        copied = await self._bot.copy_message(
            chat_id=storage_chat_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            disable_notification=True,
        )
        return copied.message_id

    async def copy_out(
        self,
        *,
        target_chat_id: int,
        storage_chat_id: int,
        storage_message_id: int,
    ) -> int:
        copied = await self._bot.copy_message(
            chat_id=target_chat_id,
            from_chat_id=storage_chat_id,
            message_id=storage_message_id,
        )
        return copied.message_id

    async def verify_storage_admin(
        self,
        *,
        storage_chat_id: int,
        bot_user_id: int,
    ) -> bool:
        member = await self._bot.get_chat_member(storage_chat_id, bot_user_id)
        if member.status == "creator":
            return True
        return member.status == "administrator" and member.can_post_messages is not False

    async def verify_user_owner(
        self,
        *,
        storage_chat_id: int,
        user_id: int,
    ) -> bool:
        member = await self._bot.get_chat_member(storage_chat_id, user_id)
        return member.status == "creator"

    async def verify_private_channel(self, storage_chat_id: int) -> bool:
        chat = await self._bot.get_chat(storage_chat_id)
        return chat.type == "channel" and chat.username is None
