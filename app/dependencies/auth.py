from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User
from app.models.car import Car
import logging

logger = logging.getLogger(__name__)

def get_current_user(
    db: Session = Depends(get_db),
    x_user_code: str = Header(..., description="User code for authentication")
) -> User:
    logger.info(f"Authenticating user with code: {x_user_code}")
    
    user = db.query(User).filter(User.user_code == x_user_code).first()
    if not user:
        logger.warning(f"User not found for code: {x_user_code}")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"User authenticated: ID {user.id}, code {user.user_code}")
    return user

def get_current_car(db: Session = Depends(get_db)) -> Car:
    car = db.query(Car).filter(Car.id == 1).first()  # Hardcoded for now
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car