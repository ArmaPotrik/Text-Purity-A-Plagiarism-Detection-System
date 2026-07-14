import uuid
from sqlalchemy import Column, Float, ForeignKey, String, DateTime, func
from .base import Base


class Result(Base):
    __tablename__ = "results"

    # 🔥 SQLite-safe UUID (fixed length)
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    file_id = Column(
        String(36),
        ForeignKey("documents.id"),
        nullable=False
    )

    matched_file_id = Column(
        String(36),
        ForeignKey("documents.id"),
        nullable=False
    )

    score = Column(Float, nullable=False)

    # 'text_similarity', 'image_similarity', 'ai_detection'
    type = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
