from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from ..core.database import Base

class ActivityType(str, Enum):
    TRANSPORT = "transport"
    ENERGY = "energy"
    WASTE = "waste"
    FOOD = "food"
    WATER = "water"

class EcoLog(Base):
    __tablename__ = "eco_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(SQLEnum(ActivityType), nullable=False)
    description = Column(Text, nullable=False)
    emissions_saved = Column(Float, nullable=False)  # kg CO2 saved
    points_earned = Column(Integer, nullable=False)
    activity_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="logs")