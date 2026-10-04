from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram.types import Message

from app.domain.value_objects.content_type import ContentType
from app.domain.value_objects.source_type import SourceType


def get_content_type(message: Message) -> ContentType:
    for attr, kind in (
        ("text", ContentType.TEXT),
        ("photo", ContentType.PHOTO),
        ("video", ContentType.VIDEO),
        ("document", ContentType.DOCUMENT),
        ("audio", ContentType.AUDIO),
        ("voice", ContentType.VOICE),
        ("video_note", ContentType.VIDEO_NOTE),
        ("animation", ContentType.ANIMATION),
        ("sticker", ContentType.STICKER),
        ("poll", ContentType.POLL),
    ):
        if getattr(message, attr, None) is not None:
            return kind
    return ContentType.OTHER


def get_searchable_text(message: Message) -> str:
    parts: list[str] = []
    if message.text:
        parts.append(message.text)
    if message.caption:
        parts.append(message.caption)
    return "\n".join(parts)


def get_source_type(message: Message) -> SourceType:
    return SourceType.FORWARDED if message.forward_origin is not None else SourceType.DIRECT
