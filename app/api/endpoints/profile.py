from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import joinedload

from ...core.database import get_db
from ...models.user import User
from ...models.log import EcoLog
from ...models.badge import UserBadge, Badge
from ..dependencies import get_current_user

router = APIRouter()

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

@router.get("/")
def get_profile(current_user: User = Depends(get_current_user)):
    print(f"🔍 DEBUG: Getting profile for user {current_user.id}")
    return current_user

@router.put("/")
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully", "user": current_user}

@router.get("/badges")
def get_user_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"🔍 DEBUG: Getting badges for user {current_user.id}")
    
    # Get user badges with badge details
    user_badges = db.query(UserBadge).options(
        joinedload(UserBadge.badge)
    ).filter(
        UserBadge.user_id == current_user.id
    ).all()
    
    print(f"🔍 DEBUG: Found {len(user_badges)} badges")
    
    # Format response
    badges_data = []
    for user_badge in user_badges:
        badges_data.append({
            "name": user_badge.badge.name,
            "description": user_badge.badge.description,
            "icon": user_badge.badge.icon,
            "earned_at": user_badge.earned_at,
            "earned": True
        })
    
    # Also include potential badges user hasn't earned yet
    all_badges = db.query(Badge).all()
    earned_badge_ids = [ub.badge_id for ub in user_badges]
    
    for badge in all_badges:
        if badge.id not in earned_badge_ids:
            badges_data.append({
                "name": badge.name,
                "description": badge.description,
                "icon": badge.icon,
                "earned_at": None,
                "earned": False
            })
    
    return {"badges": badges_data}

@router.get("/achievements")
def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"🔍 DEBUG: Getting achievements for user {current_user.id}")
    
    # Count user logs by category
    transport_count = db.query(EcoLog).filter(
        EcoLog.user_id == current_user.id,
        EcoLog.activity_type == "transport"
    ).count()
    
    energy_count = db.query(EcoLog).filter(
        EcoLog.user_id == current_user.id,
        EcoLog.activity_type == "energy"
    ).count()
    
    waste_count = db.query(EcoLog).filter(
        EcoLog.user_id == current_user.id,
        EcoLog.activity_type == "waste"
    ).count()
    
    food_count = db.query(EcoLog).filter(
        EcoLog.user_id == current_user.id,
        EcoLog.activity_type == "food"
    ).count()
    
    water_count = db.query(EcoLog).filter(
        EcoLog.user_id == current_user.id,
        EcoLog.activity_type == "water"
    ).count()
    
    total_logs = transport_count + energy_count + waste_count + food_count + water_count
    
    return {
        "achievements": [
            {"title": "Total Emissions Saved", "value": f"{current_user.total_emissions_saved:.1f} kg"},
            {"title": "Eco Score", "value": f"{current_user.eco_score} points"},
            {"title": "Total Activities", "value": total_logs},
            {"title": "Transport Activities", "value": transport_count},
            {"title": "Energy Activities", "value": energy_count},
            {"title": "Waste Activities", "value": waste_count},
            {"title": "Food Activities", "value": food_count},
            {"title": "Water Activities", "value": water_count},
        ]
    }