"""
AegisShare — ORM Models

Defines the database tables: User, ScanLog, and DlpPolicy.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """Registered user capable of scanning files."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, default="")
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="analyst", nullable=False)  # "admin" | "analyst"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # One-to-many: a user owns many scan logs.
    logs = relationship("ScanLog", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"


class ScanLog(Base):
    """Audit record created each time a file is scanned."""

    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, default=0)
    status = Column(String, nullable=False)   # "APROBADO" or "BLOQUEADO"
    risk_level = Column(String, default="none")  # "none", "low", "medium", "high", "critical"
    details = Column(JSON)
    entities_found = Column(Integer, default=0)
    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="logs")

    def __repr__(self) -> str:
        return f"<ScanLog id={self.id} file={self.filename!r} status={self.status!r}>"


class DlpPolicy(Base):
    """Configurable DLP rule that controls how entity types are handled."""

    __tablename__ = "dlp_policies"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, unique=True, nullable=False)  # e.g. "PHONE_NUMBER"
    display_name = Column(String, nullable=False)               # e.g. "Phone Number"
    action = Column(String, default="block", nullable=False)    # "block" | "warn" | "ignore"
    min_confidence = Column(Float, default=0.4, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<DlpPolicy {self.entity_type!r} action={self.action!r}>"