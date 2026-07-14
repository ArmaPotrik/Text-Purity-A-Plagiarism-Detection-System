# app/schemas.py

import uuid
from typing import Optional
from fastapi_users import schemas


# ==========================
# USER READ (Response Model)
# ==========================
class UserRead(schemas.BaseUser[uuid.UUID]):
    role: str


# ==========================
# USER CREATE (Register)
# ==========================
class UserCreate(schemas.BaseUserCreate):
    role: Optional[str] = "user"


# ==========================
# USER UPDATE
# ==========================
class UserUpdate(schemas.BaseUserUpdate):
    role: Optional[str] = None
