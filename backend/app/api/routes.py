# app/api/routes.py

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import Response
import uuid
from app.services.plagiarism import PlagiarismService
from uuid import UUID
from app.core.db import get_db
from app.core.auth import current_active_user
from app.models.user import User
from app.models.batch import Batch
from app.models.document import Document
from app.models.comparison import Comparison

from app.services.storage import StorageService
from app.services.parsing import extract_text_from_file
from app.services.ai_detection import AIDetectionService
from app.services.report import ReportService

from sqlalchemy import func
from app.models.user import User
router = APIRouter()

storage_service = StorageService()
ai_service = AIDetectionService()


# =======================
# AI CHECK (MANUAL TEXT)
# =======================
class AICheckRequest(BaseModel):
    text: str


@router.post("/ai-check")
async def check_ai_content(request: AICheckRequest):
    result = ai_service.detect(request.text)
    return {"status": "ok", "data": result}


# =======================
# DASHBOARD
# =======================
@router.get("/dashboard")
async def user_dashboard(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    batches_result = await db.execute(
        select(Batch).where(Batch.user_id == user.id)
    )
    batches = batches_result.scalars().all()

    if not batches:
        return {
            "status": "ok",
            "data": {
                "num_batches": 0,
                "num_documents": 0,
            },
        }

    batch_ids = [b.id for b in batches]

    documents_result = await db.execute(
        select(Document).where(Document.batch_id.in_(batch_ids))
    )
    documents = documents_result.scalars().all()

    return {
        "status": "ok",
        "data": {
            "num_batches": len(batches),
            "num_documents": len(documents),
        },
    }


# =======================
# DOCUMENT UPLOAD
# =======================
@router.post("/documents/upload", status_code=202)
async def upload_documents(
    files: List[UploadFile] = File(...),
    analysis_type: str = Form("both"),
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):

    # ---------------- VALIDATION ----------------
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    if analysis_type not in ["ai", "plagiarism", "both"]:
        raise HTTPException(status_code=400, detail="Invalid analysis type")

    allowed_ext = (".pdf", ".txt")
    batch_id = uuid.uuid4()

    batch = Batch(
        id=batch_id,
        user_id=user.id,
        total_docs=0,
        status="processing",
        analysis_type=analysis_type,
    )

    try:
        db.add(batch)
        await db.flush()

        documents_created = []

        # ---------------- PROCESS FILES ----------------
        for f in files:

            if not f.filename.lower().endswith(allowed_ext):
                raise HTTPException(
                    status_code=400,
                    detail="Only PDF and TXT files are allowed",
                )

            content = await f.read()

            if not content:
                raise HTTPException(
                    status_code=400,
                    detail=f"{f.filename} is empty",
                )

            storage_path = f"{batch_id}/{f.filename}"
            storage_service.save(storage_path, content)

            text_content = extract_text_from_file(content, f.filename)

            # Default AI values
            ai_score = 0.0
            ai_label = None
            is_ai_generated = False

            # ---------------- AI DETECTION ----------------
            if analysis_type in ["ai", "both"] and text_content.strip():
                ai_result = ai_service.detect(text_content)

                ai_score = float(ai_result.get("score", 0.0))
                ai_label = ai_result.get("label")
                is_ai_generated = bool(ai_result.get("is_ai", False))

            document = Document(
                batch_id=batch_id,
                filename=f.filename,
                storage_path=storage_path,
                text_content=text_content,
                ai_score=ai_score,
                ai_label=ai_label,
                is_ai_generated=is_ai_generated,
                uploaded_by=user.id,
            )

            db.add(document)
            documents_created.append(document)

        # Update batch count
        batch.total_docs = len(documents_created)
        await db.flush()

        # ---------------- PLAGIARISM DETECTION ----------------
        plagiarism_results = []

        if analysis_type in ["plagiarism", "both"] and len(documents_created) > 1:

            comparisons = PlagiarismService.compare_documents(documents_created)

            for comp in comparisons:
                db.add(comp)

                plagiarism_results.append({
    "document_1": str(comp.doc_a),
    "document_2": str(comp.doc_b),
    "similarity_score": float(comp.similarity),
})

        # Mark batch completed
        batch.status = "completed"

        await db.commit()

    except HTTPException:
        await db.rollback()
        raise

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

    # ---------------- RESPONSE ----------------
    return {
        "status": "success",
        "data": {
            "batch_id": str(batch_id),
            "analysis_type": analysis_type,
            "total_files": len(files),

            # 🔥 REQUIRED FOR FRONTEND
            "documents": [
                {
                    "filename": doc.filename,
                    "ai_score": float(doc.ai_score or 0),
                    "ai_label": doc.ai_label,
                    "is_ai_generated": bool(doc.is_ai_generated),
                }
                for doc in documents_created
            ],

            # 🔥 REQUIRED FOR FRONTEND
            "plagiarism": plagiarism_results,
        },
    }
# =======================
# EXPORT CSV
# =======================
@router.get("/batches/{batch_id}/export/csv")
async def export_csv(
    batch_id: uuid.UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    batch = await db.get(Batch, batch_id)

    if not batch or batch.user_id != user.id:
        raise HTTPException(404, "Batch not found")

    docs = await db.execute(
        select(Document).where(Document.batch_id == batch_id)
    )
    documents = docs.scalars().all()

    csv = ReportService.generate_csv_report(documents)

    return Response(
        content=csv,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=report_{batch_id}.csv"
        },
    )


# =======================
# EXPORT PDF
# =======================
@router.get("/batches/{batch_id}/export/pdf")
async def export_pdf(
    batch_id: uuid.UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    batch = await db.get(Batch, batch_id)

    if not batch or batch.user_id != user.id:
        raise HTTPException(404, "Batch not found")

    docs = await db.execute(
        select(Document).where(Document.batch_id == batch_id)
    )
    documents = docs.scalars().all()

    pdf = ReportService.generate_pdf_report(batch, documents)

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report_{batch_id}.pdf"
        },
    )


# =======================
# BATCH RESULTS
# =======================
@router.get("/batch/{batch_id}/results")
async def batch_results(
    batch_id: UUID,
    mode: str = "both",
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    batch = await db.get(Batch, batch_id)

    if not batch or batch.user_id != user.id:
        raise HTTPException(status_code=404, detail="Batch not found")

    if mode not in ["ai", "plagiarism", "both"]:
        raise HTTPException(status_code=400, detail="Invalid mode")

    response = {"status": "ok"}

    # ---------------- AI RESULTS ----------------
    if mode in ["ai", "both"]:
        ai_query = await db.execute(
            select(
                Document.id,
                Document.filename,
                Document.ai_score,
                Document.ai_label,
                Document.is_ai_generated,
            ).where(Document.batch_id == batch_id)
        )

        response["ai_results"] = [
            dict(row._mapping) for row in ai_query.all()
        ]

    # ---------------- PLAGIARISM RESULTS ----------------
    if mode in ["plagiarism", "both"]:
        plagiarism_query = await db.execute(
            select(
                Comparison.doc_a,
                Comparison.doc_b,
                Comparison.similarity,
                Comparison.details,
            ).where(Comparison.batch_id == batch_id)
        )

        response["plagiarism_results"] = [
            dict(row._mapping) for row in plagiarism_query.all()
        ]

@router.get("/admin/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
):
    total_users = await db.scalar(select(func.count()).select_from(User))
    total_batches = await db.scalar(select(func.count()).select_from(Batch))
    total_documents = await db.scalar(select(func.count()).select_from(Document))

    return {
        "status": "ok",
        "data": {
            "total_users": total_users or 0,
            "total_batches": total_batches or 0,
            "total_documents": total_documents or 0,
            "storage_usage_mb": 0.0,
            "system_status": "operational",
            "version": "1.0.0",
        },
    }

    return response
