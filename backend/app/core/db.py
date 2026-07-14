# app/core/db.py

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.core.config import settings
from app.models.user import User


# ==========================
# DATABASE ENGINE
# ==========================
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # set DEBUG=True in config for SQL logs
)


# ==========================
# SESSION FACTORY
# ==========================
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ==========================
# DB SESSION DEPENDENCY
# ==========================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# ==========================
# FASTAPI USERS DB ADAPTER
# ==========================
async def get_user_db(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, User)
