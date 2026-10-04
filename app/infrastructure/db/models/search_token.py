from uuid import UUID

from sqlalchemy import ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class SearchTokenModel(Base):
    __tablename__ = "search_tokens"

    item_id: Mapped[UUID] = mapped_column(
        ForeignKey("saved_items.id", ondelete="CASCADE"),
        primary_key=True,
    )
    token_hash: Mapped[bytes] = mapped_column(
        LargeBinary(32),
        primary_key=True,
        index=True,
    )

    item = relationship("SavedItemModel", back_populates="search_tokens")
