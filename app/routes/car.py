from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.car import Car
from app.models.user import User
from app.schemas.car_schema import CarRegisterRequest, CarResponse, CarOwnerResponse, CarPublicResponse
from app.dependencies.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v01/car", tags=["car"])

@router.post("/register", response_model=CarOwnerResponse)
def register_car(
    car_data: CarRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if license plate already exists globally (must be unique)
    existing_car = db.query(Car).filter(
        Car.license_plate == car_data.license_plate
    ).first()

    if existing_car:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "duplicate_license_plate",
                "message": "This license plate is already registered in the system"
            }
        )

    try:
        model_data = car_data.model_dump()
        model_data['owner_id'] = current_user.id

        logger.info(f"Car registration data: {model_data}")
        logger.info(f"Creating car for user_id: {current_user.id}")

        new_car = Car(**model_data)

        db.add(new_car)
        db.commit()
        db.refresh(new_car)

        logger.info(f"Car registered successfully with ID: {new_car.id}, license_plate: {new_car.license_plate}")
        return new_car

    except Exception as e:
        db.rollback()
        logger.error(f"Car registration failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@router.put("/update/{car_id}", response_model=CarOwnerResponse)
def edit_user_car(
    car_id: int,
    car_data: CarRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Edit current user's car details with ownership verification"""
    logger.info(f"Update car request: car_id={car_id}, user_id={current_user.id}")

    # Find car and verify ownership
    car = db.query(Car).filter(
        Car.id == car_id,
        Car.owner_id == current_user.id
    ).first()

    if not car:
        logger.warning(f"Car not found or not woned by user: car_id={car_id}, user_id={current_user.id}")
        raise HTTPException(status_code=404, detail="Car not found or not authorized")
    
    # Check if license plate is being changed and if new plate already exists
    if car.license_plate != car_data.license_plate:
        existing_car = db.query(Car).filter(
            Car.license_plate == car_data.license_plate,
            Car.id != car_id # Exclude current car from check
        ).first()

        if existing_car:
            raise HTTPException(status_code=409, detail="License plate already exists in the system")
    
    try:
        # Update car fields
        car.license_plate = car_data.license_plate
        car.car_brand = car_data.car_brand
        car.car_model = car_data.car_model

        db.commit()
        db.refresh(car)

        logger.info(f"Car updated successfully: {car.license_plate}")
        return car
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update car: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update car")
    

@router.get("/my-cars", response_model=list[CarOwnerResponse])
def get_user_cars(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's cars - includes license plates since owner is accessing their own data"""
    logger.info(f"Fetching cars for user_id: {current_user.id}")
    
    cars = db.query(Car).filter(Car.owner_id == current_user.id).all()
    
    logger.info(f"Found {len(cars)} cars for user_id: {current_user.id}")
    return cars

@router.get("/public/{car_id}", response_model=CarPublicResponse)
def get_public_car_info(
    car_id: int,
    db: Session = Depends(get_db)
):
    """Get minimal public car information"""
    logger.info(f"Public car info request for car_id: {car_id}")
    
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        logger.warning(f"Car not found: {car_id}")
        raise HTTPException(status_code=404, detail="Car not found")
    
    logger.info(f"Returning public info for car: {car.license_plate}")
    return CarPublicResponse.from_car(car)

@router.delete("/remove/{car_id}", response_model=dict)
def remove_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove user's car - with ownership verification"""
    logger.info(f"Remove car requests: {car_id=:}, user_id={current_user.id}")

    # Find car and verify ownership
    car = db.query(Car).filter(
        Car.id == car_id,
        Car.owner_id == current_user.id
    ).first()

    if not car:
        logger.warning(f"Car not found or not woned by user: car_id={car_id}, user_id={current_user.id}")
        raise HTTPException(status_code=404, detail="Car not found or not authorized")
    
    # Check if user has other cars (precent removing last car)
    user_car_count = db.query(Car).filter(
        Car.owner_id == current_user.id
    ).count()

    if user_car_count <= 1:
        logger.warning(f"Cannot remove last car for user_id={current_user.id}")
        raise HTTPException(
            status_code=400,
            detail="Cannot remove your only car. Please register another car first."
        )
    
    try:
        license_plate = car.license_plate
        db.delete(car)
        db.commit()

        logger.info(f"Car removed successfully: {license_plate}")
        return {
            "message": f"Car {license_plate} removed successfully!"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to remove car: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to remove car"
        )
    