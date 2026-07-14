import uuid
from sqlalchemy import Column, String, Float, DateTime, func, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID  # keep UUID for PostgreSQL compatibility
from .base import Base

class AIDetection(Base):
    __tablename__ = "ai_detection"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    model_version = Column(String)
    probability = Column(Float)
    meta_data = Column(JSON)  # <-- changed from JSONB to JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
