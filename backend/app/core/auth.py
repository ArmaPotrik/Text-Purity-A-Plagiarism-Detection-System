# app/core/auth.py

import uuid
from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from app.core.config import settings
from app.core.db import get_user_db
from app.models.user import User


SECRET = settings.SECRET_KEY


# ==========================
# USER MANAGER
# ==========================
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


# ==========================
# AUTH BACKEND (JWT)
# ==========================
bearer_transport = BearerTransport(
    tokenUrl="/api/v1/auth/jwt/login",  # ✅ MUST MATCH ROUTER PREFIX
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET,
        lifetime_seconds=60 * 60 * 24,  # 1 day
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


# ==========================
# FASTAPI USERS INSTANCE
# ==========================
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)


# ==========================
# DEPENDENCIES
# ==========================
current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(superuser=True)
