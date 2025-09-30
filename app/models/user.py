from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import uuid

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    signup_country_iso = Column(String(5), nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    user_code = Column(String(50), unique=True, default=lambda: str(uuid.uuid4()))
    profile_deep_link = Column(String(255), nullable=True)  # Deep link URL
    profile_bio = Column(Text, nullable=True)  # Optional bio text
    profile_display_name = Column(String(100), nullable=True)  # Optional display name
    qr_code_id = Column(String(50), unique=True, default=lambda: str(uuid.uuid4()))
    qr_image_path = Column(String(500), nullable=True)  # Path to generated QR image file
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    cars = relationship("Car", back_populates="owner")
    user_tier = relationship("UserTier", back_populates="user", uselist=False)
    move_requests = relationship("MoveRequest", back_populates="target_user")

