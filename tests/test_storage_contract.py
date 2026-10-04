from app.infrastructure.db.models.saved_item import SavedItemModel
from app.infrastructure.telegram.storage import TelegramStorage


def test_storage_adapter_has_user_owned_channel_checks() -> None:
    assert hasattr(TelegramStorage, "verify_private_channel")
    assert hasattr(TelegramStorage, "verify_storage_admin")
    assert hasattr(TelegramStorage, "verify_user_owner")


def test_saved_item_stores_telegram_storage_reference() -> None:
    columns = {column.name for column in SavedItemModel.__table__.columns}
    assert {"storage_chat_id", "storage_message_id"} <= columns
