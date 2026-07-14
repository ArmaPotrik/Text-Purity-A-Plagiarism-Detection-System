import uuid
from uuid import UUID

from sqlalchemy import Float, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid  # ✅ USE THIS

from .base import Base


class Comparison(Base):
    __tablename__ = "comparisons"

    id: Mapped[UUID] = mapped_column(
        Uuid,  # ✅ NOT BLOB
        primary_key=True,
        default=uuid.uuid4
    )

    batch_id: Mapped[UUID] = mapped_column(
        Uuid,  # ✅ NOT BLOB
        ForeignKey("batches.id"),
        nullable=False
    )

    doc_a: Mapped[UUID] = mapped_column(
        Uuid,  # ✅ NOT BLOB
        ForeignKey("documents.id"),
        nullable=False
    )

    doc_b: Mapped[UUID] = mapped_column(
        Uuid,  # ✅ NOT BLOB
        ForeignKey("documents.id"),
        nullable=False
    )

    similarity: Mapped[float] = mapped_column(Float, nullable=False)

    details: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
