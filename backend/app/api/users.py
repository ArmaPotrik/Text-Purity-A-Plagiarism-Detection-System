import uuid
from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.auth import auth_backend, get_user_manager
from app.core.db import get_db
from app.models.user import User
from app.models.batch import Batch
from app.models.document import Document

router = APIRouter()

# FastAPI-Users instance (NO ROUTERS HERE)
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# 📊 DASHBOARD (PROTECTED)
@router.get("/users/me/dashboard")
async def get_user_dashboard(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(fastapi_users.current_user()),
):
    batches = await db.execute(
        select(func.count(Batch.id)).where(Batch.user_id == user.id)
    )

    documents = await db.execute(
        select(func.count(Document.id))
        .join(Batch, Document.batch_id == Batch.id)
        .where(Batch.user_id == user.id)
    )

    return {
    "data": {
        "num_batches": batches.scalar_one(),
        "num_documents": documents.scalar_one(),
    }
}

