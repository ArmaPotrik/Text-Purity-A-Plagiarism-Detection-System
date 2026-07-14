import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid  # ✅ USE THIS

from app.models.base import Base


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[UUID] = mapped_column(
        Uuid,  # ✅ NOT BLOB
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid,  # ✅ NOT BLOB
        ForeignKey("users.id"),
        nullable=True,
    )

    name: Mapped[Optional[str]] = mapped_column(nullable=True)
    total_docs: Mapped[int] = mapped_column(Integer, default=0)
    processed_docs: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(default="pending")
    analysis_type: Mapped[str] = mapped_column(default="plagiarism")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
