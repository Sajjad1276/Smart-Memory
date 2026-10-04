from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, LargeBinary, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_key: Mapped[bytes] = mapped_column(LargeBinary(32), unique=True, index=True, nullable=False)
    storage_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    storage_setup_pending: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    items = relationship(
        "SavedItemModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
