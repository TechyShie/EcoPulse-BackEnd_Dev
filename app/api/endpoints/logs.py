from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...schemas.log import EcoLog, EcoLogCreate, EcoLogUpdate, EcoLogResponse
from ...models.log import EcoLog as EcoLogModel
from ...models.user import User
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[EcoLog])
def get_user_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logs = db.query(EcoLogModel).filter(
        EcoLogModel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return logs

@router.post("/", response_model=EcoLogResponse)
def create_log(
    log_data: EcoLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use AI service to calculate emissions and points
    from ...services.ai_service import calculate_co2_saved
    
    calculation = calculate_co2_saved(
        log_data.activity_type.value, 
        log_data.description,
        quantity=1.0
    )
    
    # Update user's eco score and total emissions
    current_user.eco_score += calculation["points_earned"]
    current_user.total_emissions_saved += calculation["emissions_saved"]
    
    # Create the log with calculated values (ignore any provided values)
    db_log = EcoLogModel(
        activity_type=log_data.activity_type,
        description=log_data.description,
        user_id=current_user.id,
        emissions_saved=calculation["emissions_saved"],
        points_earned=calculation["points_earned"]
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    return {"log": db_log, "message": "Log created successfully"}

@router.put("/{log_id}", response_model=EcoLogResponse)
def update_log(
    log_id: int,
    log_data: EcoLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = db.query(EcoLogModel).filter(
        EcoLogModel.id == log_id,
        EcoLogModel.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    
    for field, value in log_data.dict(exclude_unset=True).items():
        setattr(log, field, value)
    
    db.commit()
    db.refresh(log)
    return {"log": log, "message": "Log updated successfully"}

@router.delete("/{log_id}")
def delete_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = db.query(EcoLogModel).filter(
        EcoLogModel.id == log_id,
        EcoLogModel.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    
    # Update user stats
    current_user.eco_score -= log.points_earned
    current_user.total_emissions_saved -= log.emissions_saved
    
    db.delete(log)
    db.commit()
    return {"message": "Log deleted successfully"}