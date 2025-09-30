from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import logging

from app.db.base import get_db
from app.models.user import User
from app.models.car import Car
from app.models.parking_session import ParkingSession
from app.schemas.public_profile_schema import PublicProfileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v01/public_profile", tags=["public_profile"])

@router.get("/{user_code}", response_model=PublicProfileResponse)
async def get_public_profile(
    user_code: str,
    db: Session = Depends(get_db)
) -> PublicProfileResponse:
    """
    Get public profile data for scanned user.
    
    This endpoint replaces the old QR scan popup workflow and provides
    comprehensive information needed for the PublicProfilePage screen.
    No authentication required as this is public information.
    
    Args:
        user_code: 8-character user code from QR scan
        db: Database session
    
    Returns:
        PublicProfileResponse with user info, car details, and parking status
    
    Raises:
        HTTPException: 404 if user not found
        HTTPException: 422 if user has no registered cars
    """
    # Get user with their cars
    user = db.query(User).options(
        joinedload(User.cars)
    ).filter(User.user_code == user_code).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with code {user_code} not found"
        )
    
    # Check to see if the user has any registered cars
    if not user.cars:
        raise HTTPException(
            status_code=422,
            detail=f"User Code: {user_code} has no registered cars"
        )
    
    # Get the most recently registered car as active car for MVP purposes; currently lacks the "select active car" feature
    active_car = max(user.cars, key=lambda car: car.id)

    # Determine parking status by checking for active parking sessions
    active_session = db.query(ParkingSession).filter(
        ParkingSession.user_id == user.id,
        ParkingSession.end_time.is_(None)
    ).order_by(ParkingSession.start_time.desc()).first()

    if active_session:
        parking_status = "active"
        public_message = active_session.public_message
    else:
        parking_status = "notParked"
        public_message = None

    return PublicProfileResponse(
        user_code=user.user_code,
        active_car={
            "brand": active_car.car_brand,
            "model": active_car.car_model,
            "car_id": active_car.id # For internal use only
        },
        parking_status=parking_status,
        public_message=public_message
    )

@router.get("/parking_history/{user_code}", response_model=list)
async def get_public_parking_history(
    user_code: str,
    limit: int=10,
    db: Session = Depends(get_db)
) -> list:
    """
    Get public parking history for user (optional feature).
    
    This endpoint could provide insights into parking patterns
    without revealing sensitive information.
    
    Args:
        user_code: 8-character user code
        limit: Number of recent sessions to return
        db: Database session
    
    Returns:
        List of anonymized parking session data
    """
    logger.info(f"Getting public parking history for user_code: {user_code}")

    user = db.query(User).filter(User.user_code == user_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return anonymized parking data without location info
    recent_sessions = db.query(ParkingSession).filter(
        ParkingSession.user_id == user.id,
        ParkingSession.end_time.isnot(None)
    ).order_by(ParkingSession.start_time.desc()).limit(limit).all()

    anonymized_sessions = []
    for session in recent_sessions:
        anonymized_sessions.append({
            "id": session.id,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "public_message": session.public_message
        })
    
    logger.info(f"Returning {len(anonymized_sessions)} public parking sessions")

    return anonymized_sessions