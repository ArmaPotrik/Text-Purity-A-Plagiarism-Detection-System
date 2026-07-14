# app/api/auth.py

from fastapi import APIRouter

from app.core.auth import fastapi_users, auth_backend
from app.schemas import UserRead, UserCreate, UserUpdate


router = APIRouter(prefix="/auth", tags=["auth"])


# =========================
# LOGIN / LOGOUT (JWT)
# =========================
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)


# =========================
# REGISTER
# =========================
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)


# =========================
# USERS MANAGEMENT
# =========================
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)


# =========================
# RESET PASSWORD
# =========================
router.include_router(
    fastapi_users.get_reset_password_router(),
)


# =========================
# VERIFY USER
# =========================
router.include_router(
    fastapi_users.get_verify_router(UserRead),
)
