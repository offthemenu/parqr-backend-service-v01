from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone

class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    license_plate = Column(String(20), unique=True, nullable=False)
    car_brand = Column(String(50))
    car_model = Column(String(50))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    owner = relationship('User', back_populates='cars')