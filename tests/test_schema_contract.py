from app.infrastructure.db.base import Base
from app.infrastructure.db.models import (
    SavedItemModel,
    SearchTokenModel,
    UserModel,
)


def test_privacy_first_schema_has_no_raw_content_column() -> None:
    saved_columns = {column.name for column in SavedItemModel.__table__.columns}
    assert "text" not in saved_columns
    assert "caption" not in saved_columns
    assert "file_id" not in saved_columns
    assert "storage_message_id" in saved_columns
    assert "storage_chat_id" in saved_columns


def test_user_storage_is_user_owned_and_optional() -> None:
    storage_column = UserModel.__table__.c.storage_chat_id
    assert storage_column.nullable is True
    assert "storage_setup_pending" in {
        column.name for column in UserModel.__table__.columns
    }


def test_saved_item_storage_is_required() -> None:
    storage_column = SavedItemModel.__table__.c.storage_chat_id
    assert storage_column.nullable is False


def test_only_three_persistent_tables_exist_in_foundation() -> None:
    assert set(Base.metadata.tables) == {
        "users",
        "saved_items",
        "search_tokens",
    }


def test_search_token_is_scoped_to_item() -> None:
    primary_keys = [
        column.name for column in SearchTokenModel.__table__.primary_key.columns
    ]
    assert primary_keys == ["item_id", "token_hash"]
