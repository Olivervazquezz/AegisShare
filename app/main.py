"""
AegisShare — FastAPI Application

Main module that wires together routes, authentication, DLP scanning,
and the static-file server.
"""

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import database, models, security
from .services import dlp

# ---------------------------------------------------------------------------
# Application bootstrap
# ---------------------------------------------------------------------------
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="AegisShare",
    description="AI-Powered Data Loss Prevention platform.",
    version="1.0.0",
)

# Serve static assets (CSS, JS, images).
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# OAuth2 token endpoint path.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
def get_db():
    """Yield a database session that is closed after the request."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """Decode the JWT and return the authenticated user, or raise 401."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


# ---------------------------------------------------------------------------
# Routes — Public
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
def serve_spa():
    """Serve the single-page frontend."""
    return FileResponse("app/static/index.html")


@app.post("/token", summary="Obtain access token")
def login_for_access_token(
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


# ---------------------------------------------------------------------------
# Routes — Authenticated
# ---------------------------------------------------------------------------
@app.post("/users/", summary="Create user (admin)")
def create_user(
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    """Register a new user with hashed credentials.

    .. warning:: This endpoint has no auth guard — secure it before
       deploying to production.
    """
    existing = (
        db.query(models.User).filter(models.User.email == email).first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado.",
        )

    new_user = models.User(
        email=email,
        hashed_password=security.get_password_hash(password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"mensaje": "Usuario creado", "email": new_user.email}


@app.get("/users/me", summary="Get current user profile")
def read_current_user(
    current_user: models.User = Depends(get_current_user),
):
    """Return the profile of the currently authenticated user."""
    return {
        "email": current_user.email,
        "estado": "Autenticado y Seguro",
    }


@app.post("/scan/", summary="Scan file for PII")
async def scan_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a text file, run DLP analysis, and log the result."""
    content = await file.read()

    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Solo se aceptan archivos de texto (UTF-8).",
        )

    is_safe, risks = dlp.is_safe(text_content)
    estado = "APROBADO ✅" if is_safe else "BLOQUEADO ❌"
    details = risks if not is_safe else [{"mensaje": "Limpio"}]

    # Persist audit log.
    log_entry = models.ScanLog(
        filename=file.filename,
        status=estado,
        details=details,
        user_id=current_user.id,
    )
    db.add(log_entry)
    db.commit()

    return {
        "archivo": file.filename,
        "analisis_ia": estado,
        "detalles": details,
        "auditor": current_user.email,
    }


@app.get("/history/", summary="Get scan history")
def get_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the last 10 scans for the authenticated user."""
    logs = (
        db.query(models.ScanLog)
        .filter(models.ScanLog.user_id == current_user.id)
        .order_by(models.ScanLog.id.desc())
        .limit(10)
        .all()
    )
    return logs