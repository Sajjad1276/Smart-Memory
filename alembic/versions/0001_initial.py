"""initial privacy-first schema"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_key", sa.LargeBinary(length=32), nullable=False),
        sa.Column("storage_chat_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "storage_setup_pending",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_user_key", "users", ["user_key"], unique=True)

    op.create_table(
        "saved_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_key", sa.LargeBinary(length=32), nullable=False),
        sa.Column("storage_message_id", sa.BigInteger(), nullable=False),
        sa.Column("content_type", sa.String(length=32), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column(
            "saved_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_saved_items_user_id", "saved_items", ["user_id"])
    op.create_index(
        "ix_saved_items_event_key", "saved_items", ["event_key"], unique=True
    )
    op.create_index(
        "ix_saved_items_storage_message_id",
        "saved_items",
        ["storage_message_id"],
    )
    op.create_index("ix_saved_items_saved_at", "saved_items", ["saved_at"])

    op.create_table(
        "search_tokens",
        sa.Column(
            "item_id",
            sa.Uuid(),
            sa.ForeignKey("saved_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.LargeBinary(length=32), nullable=False),
        sa.PrimaryKeyConstraint(
            "item_id",
            "token_hash",
            name="pk_search_tokens",
        ),
    )
    op.create_index(
        "ix_search_tokens_token_hash",
        "search_tokens",
        ["token_hash"],
    )


def downgrade() -> None:
    op.drop_index("ix_search_tokens_token_hash", table_name="search_tokens")
    op.drop_table("search_tokens")
    op.drop_index("ix_saved_items_saved_at", table_name="saved_items")
    op.drop_index(
        "ix_saved_items_storage_message_id",
        table_name="saved_items",
    )
    op.drop_index("ix_saved_items_event_key", table_name="saved_items")
    op.drop_index("ix_saved_items_user_id", table_name="saved_items")
    op.drop_table("saved_items")
    op.drop_index("ix_users_user_key", table_name="users")
    op.drop_table("users")
