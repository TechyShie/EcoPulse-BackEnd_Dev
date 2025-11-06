from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ActivityType(str, Enum):
    TRANSPORT = "transport"
    ENERGY = "energy"
    WASTE = "waste"
    FOOD = "food"
    WATER = "water"

class EcoLogBase(BaseModel):
    activity_type: ActivityType
    description: str

class EcoLogCreate(EcoLogBase):
    pass

class EcoLogUpdate(BaseModel):
    activity_type: Optional[ActivityType] = None
    description: Optional[str] = None

class EcoLog(EcoLogBase):
    id: int
    user_id: int
    emissions_saved: float
    points_earned: int
    activity_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class EcoLogResponse(BaseModel):
    log: EcoLog
    message: str