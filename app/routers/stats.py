"""
AegisShare — Stats Router

Provides dashboard KPIs and daily scan/threat counts.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats/", response_model=schemas.StatsResponse, summary="Dashboard statistics")
def get_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return aggregate KPIs and a 7-day scan trend for the dashboard."""
    query = db.query(models.ScanLog)

    # Analysts see only their own stats.
    if current_user.role != "admin":
        query = query.filter(models.ScanLog.user_id == current_user.id)

    total_scans = query.count()
    threats_blocked = query.filter(models.ScanLog.status == "BLOQUEADO").count()
    approval_rate = ((total_scans - threats_blocked) / total_scans * 100) if total_scans > 0 else 100.0

    # Scans today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    scans_today = query.filter(models.ScanLog.timestamp >= today_start).count()

    # Daily breakdown (last 7 days)
    daily = []
    for i in range(6, -1, -1):
        day = today_start - timedelta(days=i)
        next_day = day + timedelta(days=1)

        day_scans = query.filter(
            models.ScanLog.timestamp >= day,
            models.ScanLog.timestamp < next_day,
        ).count()

        day_threats = query.filter(
            models.ScanLog.timestamp >= day,
            models.ScanLog.timestamp < next_day,
            models.ScanLog.status == "BLOQUEADO",
        ).count()

        daily.append(schemas.DailyCount(
            date=day.strftime("%Y-%m-%d"),
            scans=day_scans,
            threats=day_threats,
        ))

    return schemas.StatsResponse(
        total_scans=total_scans,
        threats_blocked=threats_blocked,
        approval_rate=round(approval_rate, 1),
        scans_today=scans_today,
        daily=daily,
    )
