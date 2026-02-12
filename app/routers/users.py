"""
AegisShare — Users Router

User management (admin-only).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..dependencies import get_db, require_admin

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/users/", response_model=list[schemas.UserOut], summary="List all users")
def list_users(
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return all registered users (admin-only)."""
    return db.query(models.User).order_by(models.User.id).all()


@router.post(
    "/users/",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
)
def create_user(
    body: schemas.UserCreate,
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Register a new user (admin-only)."""
    existing = db.query(models.User).filter(models.User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado.",
        )

    new_user = models.User(
        email=body.email,
        full_name=body.full_name,
        hashed_password=security.get_password_hash(body.password),
        role=body.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
