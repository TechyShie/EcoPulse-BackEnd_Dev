from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ...core.database import get_db
from ...models.user import User
from ...models.log import EcoLog
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"🔍 DEBUG: Getting stats for user {current_user.id}")
    
    # Count total logs for this user
    total_activities = db.query(EcoLog).filter(
        EcoLog.user_id == current_user.id
    ).count()
    
    # Weekly trend data - last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    weekly_logs = db.query(EcoLog).filter(
        EcoLog.user_id == current_user.id,
        EcoLog.activity_date >= week_ago
    ).all()
    
    weekly_emissions = sum(log.emissions_saved for log in weekly_logs)
    weekly_activity_count = len(weekly_logs)
    
    # Calculate user rank based on eco_score
    if current_user.eco_score >= 200:
        user_rank = "Eco Champion"
    elif current_user.eco_score >= 100:
        user_rank = "Eco Warrior" 
    elif current_user.eco_score >= 50:
        user_rank = "Eco Enthusiast"
    else:
        user_rank = "Eco Beginner"
    
    return {
        "total_emissions_saved": current_user.total_emissions_saved or 0,
        "eco_score": current_user.eco_score or 0,
        "weekly_emissions_saved": weekly_emissions,
        "weekly_activity_count": weekly_activity_count,
        "user_rank": user_rank
    }

@router.get("/activities")
def get_recent_activities(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"🔍 DEBUG: Getting activities for user {current_user.id}")
    
    activities = db.query(EcoLog).filter(
        EcoLog.user_id == current_user.id
    ).order_by(EcoLog.activity_date.desc()).offset(skip).limit(limit).all()
    
    print(f"🔍 DEBUG: Found {len(activities)} activities")
    
    return activities