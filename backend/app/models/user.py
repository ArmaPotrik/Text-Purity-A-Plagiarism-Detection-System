# app/models/user.py

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

from app.models.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    # Additional custom field
    role: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="user",
    )
