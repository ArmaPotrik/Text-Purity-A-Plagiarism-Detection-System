import uuid
from uuid import UUID

from sqlalchemy import (Text,DateTime,func,Float,
Boolean,
    ForeignKey,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid  # ✅ USE THIS

from .base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    batch_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("batches.id"),
        nullable=False,
    )

    filename: Mapped[str] = mapped_column(String, nullable=False)

    storage_path: Mapped[str] = mapped_column(String, nullable=False)

    content_hash: Mapped[str | None] = mapped_column(String)
    mime_type: Mapped[str | None] = mapped_column(String)
    text_content: Mapped[str | None] = mapped_column(Text)

    ai_score: Mapped[float] = mapped_column(Float, default=0.0)
    ai_label: Mapped[str | None] = mapped_column(String)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)

    uploaded_by: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False,
    )
