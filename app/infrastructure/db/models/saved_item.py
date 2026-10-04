from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class SavedItemModel(Base):
    __tablename__ = "saved_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    event_key: Mapped[bytes] = mapped_column(
        LargeBinary(32),
        unique=True,
        index=True,
        nullable=False,
    )
    storage_message_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )
    content_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )

    user = relationship("UserModel", back_populates="items")
    search_tokens = relationship(
        "SearchTokenModel",
        back_populates="item",
        cascade="all, delete-orphan",
    )
