from types import SimpleNamespace

from app.application.services.message_inspector import (
    get_content_type,
    get_searchable_text,
    get_source_type,
)
from app.domain.value_objects.content_type import ContentType
from app.domain.value_objects.source_type import SourceType


def test_text_message() -> None:
    message = SimpleNamespace(
        text="hello",
        caption=None,
        photo=None,
        video=None,
        document=None,
        audio=None,
        voice=None,
        video_note=None,
        animation=None,
        sticker=None,
        poll=None,
        forward_origin=None,
    )
    assert get_content_type(message) is ContentType.TEXT
    assert get_searchable_text(message) == "hello"
    assert get_source_type(message) is SourceType.DIRECT
