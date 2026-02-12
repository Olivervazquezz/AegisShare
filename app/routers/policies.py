"""
AegisShare — Policies Router

CRUD for DLP policies (admin-only).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_user, require_admin

router = APIRouter(prefix="/api", tags=["policies"])


@router.get("/policies/", response_model=list[schemas.PolicyOut], summary="List DLP policies")
def list_policies(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all DLP policies (visible to any authenticated user)."""
    return db.query(models.DlpPolicy).order_by(models.DlpPolicy.entity_type).all()


@router.post(
    "/policies/",
    response_model=schemas.PolicyOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create DLP policy",
)
def create_policy(
    body: schemas.PolicyCreate,
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new DLP policy (admin-only)."""
    existing = (
        db.query(models.DlpPolicy)
        .filter(models.DlpPolicy.entity_type == body.entity_type)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una política para '{body.entity_type}'.",
        )

    policy = models.DlpPolicy(**body.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.put("/policies/{policy_id}", response_model=schemas.PolicyOut, summary="Update DLP policy")
def update_policy(
    policy_id: int,
    body: schemas.PolicyUpdate,
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update an existing DLP policy (admin-only)."""
    policy = db.query(models.DlpPolicy).filter(models.DlpPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Política no encontrada.")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(policy, field, value)

    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete DLP policy")
def delete_policy(
    policy_id: int,
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a DLP policy (admin-only)."""
    policy = db.query(models.DlpPolicy).filter(models.DlpPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Política no encontrada.")

    db.delete(policy)
    db.commit()
