from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class MoveRequest(Base):
    __tablename__ = "move_requests"

    id = Column(Integer, primary_key=True, index=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # If the sender is a ParQR user, simplified to anon for MVP
    # message = Column(Text, nullable=True) # Optional custom message (not available on MVP rollout; likely freemium linked with the whole chat function)
    ip_address = Column(String(45), nullable=False) #IPv6
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    viewed_at = Column(DateTime, nullable=True)
    license_plate = Column(String(20), nullable=False) # Required for parkout
    is_read = Column(Boolean, default=False, nullable=False) # For Notification Badging 
    requester_info = Column(String(100), nullable=True) # Anonymous Requester identifier

    # Relationships
    target_user = relationship("User", back_populates="move_requests")

