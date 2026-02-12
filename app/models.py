"""
AegisShare — ORM Models

Defines the ``User`` and ``ScanLog`` tables used by the application.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """Registered user capable of scanning files."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # One-to-many: a user owns many scan logs.
    logs = relationship("ScanLog", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class ScanLog(Base):
    """Audit record created each time a file is scanned."""

    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False)   # "APROBADO ✅" or "BLOQUEADO ❌"
    details = Column(JSON)                    # Full DLP analysis payload
    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="logs")

    def __repr__(self) -> str:
        return f"<ScanLog id={self.id} file={self.filename!r} status={self.status!r}>"