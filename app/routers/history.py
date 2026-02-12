"""
AegisShare — History Router

Provides paginated, filterable access to the scan audit log.
"""

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history/", response_model=schemas.PaginatedHistory, summary="Scan history")
def get_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return paginated scan history for the authenticated user.

    Supports filtering by status and searching by filename.
    Admin users can see all scans.
    """
    query = db.query(models.ScanLog)

    # Admins see everything; analysts see only their own scans.
    if current_user.role != "admin":
        query = query.filter(models.ScanLog.user_id == current_user.id)

    if status_filter:
        query = query.filter(models.ScanLog.status == status_filter.upper())

    if search:
        query = query.filter(models.ScanLog.filename.ilike(f"%{search}%"))

    total = query.count()
    pages = max(1, (total + per_page - 1) // per_page)

    logs = (
        query.order_by(models.ScanLog.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    items = []
    for log in logs:
        owner = db.query(models.User).filter(models.User.id == log.user_id).first()
        items.append(
            schemas.HistoryItem(
                id=log.id,
                filename=log.filename,
                file_size=log.file_size or 0,
                status=log.status,
                risk_level=log.risk_level or "none",
                entities_found=log.entities_found or 0,
                timestamp=log.timestamp,
                user_email=owner.email if owner else "",
            )
        )

    return schemas.PaginatedHistory(items=items, total=total, page=page, pages=pages)


@router.get("/history/export", summary="Export history as CSV")
def export_history_csv(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download the full scan history as a CSV file."""
    query = db.query(models.ScanLog)

    if current_user.role != "admin":
        query = query.filter(models.ScanLog.user_id == current_user.id)

    logs = query.order_by(models.ScanLog.id.desc()).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["ID", "Filename", "Status", "Risk Level", "Entities", "Date"])

    for log in logs:
        writer.writerow([
            log.id,
            log.filename,
            log.status,
            log.risk_level or "none",
            log.entities_found or 0,
            log.timestamp.isoformat() if log.timestamp else "",
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=aegisshare_history.csv"},
    )
