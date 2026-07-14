import uuid
from sqlalchemy import Column, Integer, String, DateTime, func
from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    # 🔥 SQLite-safe UUID (fixed length)
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # 'process_text_upload', 'process_image_upload'
    task_type = Column(String, nullable=False)

    # 'pending', 'processing', 'completed', 'failed'
    status = Column(String, nullable=False, default="pending")

    progress = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
