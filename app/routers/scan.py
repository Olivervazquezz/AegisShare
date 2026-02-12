"""
AegisShare — Scan Router

Handles file uploads and DLP analysis.
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_user
from ..services import dlp

router = APIRouter(prefix="/api", tags=["scan"])


@router.post("/scan/", response_model=schemas.ScanResult, summary="Scan file for PII")
async def scan_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a text file, run DLP analysis against active policies, and log the result."""
    content = await file.read()
    file_size = len(content)

    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Solo se aceptan archivos de texto (UTF-8).",
        )

    # Load active policies from DB.
    policies = (
        db.query(models.DlpPolicy)
        .filter(models.DlpPolicy.is_active == True)  # noqa: E712
        .all()
    )

    is_safe, risks, risk_level = dlp.analyze_with_policies(text_content, policies)
    estado = "APROBADO" if is_safe else "BLOQUEADO"
    details = risks if risks else [{"mensaje": "Limpio — Sin datos sensibles detectados."}]

    # Persist audit log.
    log_entry = models.ScanLog(
        filename=file.filename,
        file_size=file_size,
        status=estado,
        risk_level=risk_level,
        details=details,
        entities_found=len(risks),
        user_id=current_user.id,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    return schemas.ScanResult(
        id=log_entry.id,
        archivo=file.filename,
        analisis_ia=estado,
        risk_level=risk_level,
        detalles=details,
        entities_found=len(risks),
        auditor=current_user.email,
    )
