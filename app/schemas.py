"""
AegisShare — Pydantic Schemas

Request/response models used by the API routers.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = ""
    role: str = Field(default="analyst", pattern="^(admin|analyst)$")


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------
class ScanResult(BaseModel):
    id: int
    archivo: str
    analisis_ia: str
    risk_level: str
    detalles: list[dict[str, Any]]
    entities_found: int
    auditor: str


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------
class HistoryItem(BaseModel):
    id: int
    filename: str
    file_size: int
    status: str
    risk_level: str
    entities_found: int
    timestamp: datetime
    user_email: str = ""

    model_config = {"from_attributes": True}


class PaginatedHistory(BaseModel):
    items: list[HistoryItem]
    total: int
    page: int
    pages: int


# ---------------------------------------------------------------------------
# Stats (Dashboard KPIs)
# ---------------------------------------------------------------------------
class DailyCount(BaseModel):
    date: str
    scans: int
    threats: int


class StatsResponse(BaseModel):
    total_scans: int
    threats_blocked: int
    approval_rate: float
    scans_today: int
    daily: list[DailyCount]


# ---------------------------------------------------------------------------
# DLP Policies
# ---------------------------------------------------------------------------
class PolicyCreate(BaseModel):
    entity_type: str = Field(..., min_length=1)
    display_name: str = Field(..., min_length=1)
    action: str = Field(default="block", pattern="^(block|warn|ignore)$")
    min_confidence: float = Field(default=0.4, ge=0.0, le=1.0)
    is_active: bool = True


class PolicyUpdate(BaseModel):
    display_name: str | None = None
    action: str | None = Field(default=None, pattern="^(block|warn|ignore)$")
    min_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    is_active: bool | None = None


class PolicyOut(BaseModel):
    id: int
    entity_type: str
    display_name: str
    action: str
    min_confidence: float
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
