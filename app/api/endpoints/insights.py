from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import defaultdict

from ...core.database import get_db
from ...models.user import User
from ...models.log import EcoLog, ActivityType
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/weekly")
def get_weekly_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get data for the last 4 weeks
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(weeks=4)
    
    weekly_data = db.query(
        func.strftime('%Y-%W', EcoLog.activity_date).label('week'),
        func.sum(EcoLog.emissions_saved).label('emissions'),
        func.sum(EcoLog.points_earned).label('points')
    ).filter(
        EcoLog.user_id == current_user.id,
        EcoLog.activity_date >= start_date
    ).group_by('week').all()
    
    return {
        "weekly_progress": [
            {
                "week": data.week,
                "emissions_saved": data.emissions or 0,
                "points_earned": data.points or 0
            }
            for data in weekly_data
        ]
    }

@router.get("/categories")
def get_category_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category_data = db.query(
        EcoLog.activity_type,
        func.count(EcoLog.id).label('count'),
        func.sum(EcoLog.emissions_saved).label('emissions')
    ).filter(
        EcoLog.user_id == current_user.id
    ).group_by(EcoLog.activity_type).all()
    
    return {
        "categories": [
            {
                "type": data.activity_type,
                "count": data.count,
                "total_emissions": data.emissions or 0
            }
            for data in category_data
        ]
    }

@router.get("/summary")
def get_monthly_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_data = db.query(
        func.sum(EcoLog.emissions_saved).label('monthly_emissions'),
        func.sum(EcoLog.points_earned).label('monthly_points'),
        func.count(EcoLog.id).label('activity_count')
    ).filter(
        EcoLog.user_id == current_user.id,
        EcoLog.activity_date >= current_month
    ).first()
    
    return {
        "monthly_emissions_saved": monthly_data.monthly_emissions or 0,
        "monthly_points_earned": monthly_data.monthly_points or 0,
        "monthly_activities": monthly_data.activity_count or 0
    }