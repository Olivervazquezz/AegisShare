"""
AegisShare — Auth Router

Handles login (token generation) and current-user profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, security, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/token", response_model=schemas.TokenResponse, summary="Obtain access token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate with email + password and receive a JWT."""
    user = (
        db.query(models.User)
        .filter(models.User.email == form_data.username)
        .first()
    )

    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
        )

    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=schemas.UserOut, summary="Current user profile")
def me(current_user: models.User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user
