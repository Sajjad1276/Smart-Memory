"""store the storage channel on each saved item"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_storage_chat_per_item"
down_revision: Union[str, Sequence[str], None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "saved_items",
        sa.Column("storage_chat_id", sa.BigInteger(), nullable=True),
    )
    op.execute(
        """
        UPDATE saved_items AS item
        SET storage_chat_id = users.storage_chat_id
        FROM users
        WHERE users.id = item.user_id
        """
    )
    op.alter_column(
        "saved_items",
        "storage_chat_id",
        existing_type=sa.BigInteger(),
        nullable=False,
    )
    op.create_index(
        "ix_saved_items_storage_chat_id",
        "saved_items",
        ["storage_chat_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_saved_items_storage_chat_id",
        table_name="saved_items",
    )
    op.drop_column("saved_items", "storage_chat_id")
