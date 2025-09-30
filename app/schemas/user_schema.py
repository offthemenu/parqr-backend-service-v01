from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class UserRegisterRequest(BaseModel):
    phone_number: str
    signup_country_iso: str

class UserResponse(BaseModel):
    id: int
    user_code: str
    qr_code_id: Optional[str] = None
    created_at: datetime
    signup_country_iso: str
    qr_image_path: Optional[str] = None
    # Note: phone_number deliberately excluded for privacy
    
    model_config = {"from_attributes": True}

class UserPublicResponse(BaseModel):
    """Ultra-minimal user data for public API calls"""
    user_code: str
    qr_code_id: Optional[str] = None
    signup_country_iso: str
    
    model_config = {"from_attributes": True}

class UserWithCarsResponse(BaseModel):
    """User data with associated cars (for sign-in flow)"""

    id: int
    user_code: str
    qr_code_id: str
    created_at: datetime
    signup_country_iso: str
    qr_image_path: Optional[str] = None
    profile_deep_link: Optional[str] = None
    profile_bio: Optional[str] = None
    profile_display_name: Optional[str] = None
    user_tier: str = "basic"  # User tier for feature gating
    cars: list[dict] = [] # populated with car data
    parking_status: Literal["active", "not_parked"] = "not_parked"
    public_message: Optional[str] = None

    model_config = {"from_attributes": True}