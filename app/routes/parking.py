from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.schemas.parking_schema import ParkingSessionCreate, ParkingSessionOut, ParkingSessionEnd
from typing import List
from app.models.parking_session import ParkingSession
from app.db.base import get_db
from app.dependencies.auth import get_current_user
from app.models.car import Car
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v01/parking")

@router.post("/start", response_model=ParkingSessionOut)
def start_parking(
    session_data: ParkingSessionCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(f"Starting parking session for user_id: {current_user.id}, car_id: {session_data.car_id}")
    
    # Verify car ownership
    car = db.query(Car).filter(
        Car.id == session_data.car_id,
        Car.owner_id == current_user.id
    ).first()
    
    if not car:
        logger.warning(f"Car not found or not owned by user: car_id={session_data.car_id}, user_id={current_user.id}")
        raise HTTPException(status_code=404, detail="Car not found")
    
    parking_data = session_data.model_dump()
    logger.info(f"Parking session data: {parking_data}")
    
    start_time = datetime.now(timezone.utc)
    new_session = ParkingSession(
        user_id=current_user.id,
        car_id=session_data.car_id,
        start_time=start_time,
        note_location=session_data.note_location,
        public_message=session_data.public_message,
        latitude=session_data.latitude,
        longitude=session_data.longitude
    )
    
    logger.info(f"Creating parking session at {start_time}")
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    # Ensure timezone is included in the response
    if new_session.start_time.tzinfo is None:
        new_session.start_time = new_session.start_time.replace(tzinfo=timezone.utc)
    
    logger.info(f"Parking session started successfully with ID: {new_session.id}")
    return new_session

@router.post("/end", response_model=ParkingSessionOut)
def end_parking(
    data: ParkingSessionEnd,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(f"Ending parking session request for session_id: {data.session_id}, user_id: {current_user.id}")
    
    # Verify session exists and belongs to current user
    session = db.query(ParkingSession).filter(
        ParkingSession.id == data.session_id,
        ParkingSession.user_id == current_user.id
    ).first()
    
    if not session:
        logger.warning(f"Parking session not found or not owned by user: session_id={data.session_id}, user_id={current_user.id}")
        raise HTTPException(status_code=404, detail="Parking session not found")
    
    end_time = datetime.now(timezone.utc)
    session.end_time = end_time
    
    # Ensure both datetimes are timezone-aware for calculation
    start_time_aware = session.start_time.replace(tzinfo=timezone.utc) if session.start_time.tzinfo is None else session.start_time
    duration = end_time - start_time_aware
    logger.info(f"Ending parking session {data.session_id} at {end_time}, duration: {duration}")
    
    db.commit()
    db.refresh(session)
    
    # Ensure timezone is included in the response
    if session.start_time.tzinfo is None:
        session.start_time = session.start_time.replace(tzinfo=timezone.utc)
    if session.end_time and session.end_time.tzinfo is None:
        session.end_time = session.end_time.replace(tzinfo=timezone.utc)
    
    logger.info(f"Parking session ended successfully: {data.session_id}")
    return session

@router.get("/active")
def get_active_sessions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(f"Getting active parking sessions for user_id: {current_user.id}")
    
    # Get active sessions (end_time is null) for the current user
    active_sessions = db.query(ParkingSession).filter(
        ParkingSession.user_id == current_user.id,
        ParkingSession.end_time.is_(None)
    ).all()
    
    # Ensure timezone is included in the response for all sessions
    for session in active_sessions:
        if session.start_time.tzinfo is None:
            session.start_time = session.start_time.replace(tzinfo=timezone.utc)
        if session.end_time and session.end_time.tzinfo is None:
            session.end_time = session.end_time.replace(tzinfo=timezone.utc)
    
    logger.info(f"Found {len(active_sessions)} active sessions for user {current_user.id}")
    
    return {"active_sessions": active_sessions}

@router.get("/history", response_model=List[ParkingSessionOut])
def get_parking_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
        Get user's parking history with optional limit
    """
    logger.info(f"Getting parking history for user: {current_user.id}, limit: {limit}")

    sessions = db.query(ParkingSession).filter(
        ParkingSession.user_id == current_user.id
    ).order_by(
        ParkingSession.start_time.desc()
    ).limit(limit).all()

    logger.info(f"Found {len(sessions)} parking sessions")
    return sessions