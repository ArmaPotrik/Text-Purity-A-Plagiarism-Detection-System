# app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.api.auth import router as auth_router
from app.core.db import engine
from app.models.base import Base


# ==========================
# LIFESPAN (DB INIT)
# ==========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


# ==========================
# CORS
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # adjust if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================
# ROUTERS
# ==========================
app.include_router(auth_router, prefix="/api/v1")
app.include_router(api_router, prefix="/api/v1")


# ==========================
# ROOT ENDPOINTS
# ==========================
@app.get("/")
async def root():
    return {"message": "Server is running!"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
