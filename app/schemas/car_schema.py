from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re

class CarRegisterRequest(BaseModel):
    license_plate: str
    car_brand: str
    car_model: str

    @field_validator('license_plate')
    def validate_korean_license_plate(cls, v):
        # Korean license plate format: 123가4567 or 123나4567, etc.
        korean_plate_pattern = r'^\d{2,3}[가-힣]\d{4}$'

        if not re.match(korean_plate_pattern, v):
            raise ValueError('License plate must follow Korean format (e.g., 123가4567)')

        return v

    @field_validator('car_brand')
    def validate_car_brand(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Car brand must be at least 2 characters')
        return v.strip().title()

    @field_validator('car_model')
    def validate_car_model(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Car model is required')
        return v.strip().title()


class CarOwnerResponse(BaseModel):
    """Full car data for owner only - includes sensitive license plate"""
    id: int
    license_plate: str
    car_brand: str
    car_model: str
    created_at: datetime
    # Note: owner_id excluded for privacy
    
    model_config = {"from_attributes": True}

class CarResponse(BaseModel):
    """Privacy-preserving car data for shared contexts - excludes license plate"""
    id: int
    car_brand: str
    car_model: str
    created_at: datetime
    # Note: license_plate and owner_id excluded for privacy
    
    model_config = {"from_attributes": True}

class CarPublicResponse(BaseModel):
    """Minimal car data for public API calls"""
    car_id: int
    car_brand: str
    car_model: str
    
    model_config = {"from_attributes": True}
    
    @classmethod
    def from_car(cls, car):
        return cls(
            car_id=car.id,
            car_brand=car.car_brand,
            car_model=car.car_model
        )