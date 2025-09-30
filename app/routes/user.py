from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User
from app.models.car import Car
from app.models.parking_session import ParkingSession
from app.schemas.user_schema import UserRegisterRequest, UserResponse, UserPublicResponse, UserWithCarsResponse
from app.dependencies.auth import get_current_user
from app.services.qr_service import QRCodeService
import secrets
import string
import hashlib
import uuid
import logging
import sys
from pathlib import Path
import os

load_dotenv(override=True)

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from country_codes import get_servicing_countries_list, is_valid_country_iso

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v01/user", tags=["user"])

def generate_user_code() -> str:
    """Generate 8-character alphanumeric user code"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

def generate_qr_code_id(user_code: str, phone_number: str) -> str:
    """
    Generate unique QR code ID based on user data
    Format: QR_[8-char-hash] for easy identification
    """
    # Create unique string from user data + timestamp
    unique_string = f"{user_code}_{phone_number}_{uuid.uuid4().hex[:8]}"
    
    # Generate SHA-256 hash and take first 8 characters
    hash_object = hashlib.sha256(unique_string.encode())
    short_hash = hash_object.hexdigest()[:8].upper()
    
    return f"QR_{short_hash}"

@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"User registration attempt for phone: {user_data.phone_number}, country: {user_data.signup_country_iso}")
    
    # Validate country ISO code
    if not is_valid_country_iso(user_data.signup_country_iso):
        raise HTTPException(status_code=400, detail="Invalid country code - country not serviced")
    
    # Basic validation for Korean mobile format (assuming South Korea for now)
    if user_data.signup_country_iso.upper() == "KR":
        if len(user_data.phone_number) != 11:
            raise HTTPException(status_code=400, detail="Phone number must be 11 digits")
        
        if not user_data.phone_number.isdigit():
            raise HTTPException(status_code=400, detail="Phone number must contain only digits")
        
        if not user_data.phone_number.startswith("010"):
            raise HTTPException(status_code=400, detail="Invalid mobile phone number format")
        
        # Transform to international format
        phone_number_parse = user_data.phone_number[1:]
        phone_number_clean = f"+82{phone_number_parse}"
    else:
        # For other countries, basic validation for now
        if not user_data.phone_number.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise HTTPException(status_code=400, detail="Phone number must contain only digits and valid separators")
        
        # Store as-is for other countries (will enhance later)
        phone_number_clean = user_data.phone_number
    
    # Check if phone number already exists
    existing_user = db.query(User).filter(User.phone_number == phone_number_clean).first()
    if existing_user:
        logger.warning(f"Registration failed - phone number already exists: {user_data.phone_number}")
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Generate unique user_code
    user_code = generate_user_code()
    while db.query(User).filter(User.user_code == user_code).first():
        logger.debug(f"User code collision, regenerating: {user_code}")
        user_code = generate_user_code()
    
    # Generate QR code ID 
    qr_code_id = generate_qr_code_id(user_code, phone_number_clean)

    # Generate profile deep link URL
    if os.getenv("DEV_MODE", "false").lower() == "true":
        profile_deep_link = f"exp://192.168.1.39:19006/--/profile/{user_code}"
    else:
        # production deep link when ready. Placeholder for now.
        profile_deep_link = f"https://parqr.app/profile/{user_code}"
    
    logger.info(f"Generated user_code: {user_code}, qr_code_id: {qr_code_id}")

    # Generate QR code image for physical card before saving user
    try:
        qr_image_path = QRCodeService.generate_profile_qr_image(
            user_code=user_code,
            qr_code_id=qr_code_id,
            profile_url=profile_deep_link,
            display_name=user_code  # Using user_code as default display name
        )
        logger.info(f"Generated QR image: {qr_image_path}")
    except Exception as e:
        logger.error(f"Failed to generate QR image for {user_code}: {str(e)}")
        # Set to None if QR generation fails - don't block user registration
        qr_image_path = None
    
    new_user = User(
        phone_number=phone_number_clean,
        user_code=user_code,
        qr_code_id=qr_code_id,
        signup_country_iso=user_data.signup_country_iso.upper(),
        profile_deep_link=profile_deep_link,
        profile_display_name=user_code,
        profile_bio=None,
        qr_image_path=qr_image_path
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"User registered successfully with ID: {new_user.id}")
    return new_user

@router.get("/profile", response_model=UserResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile - phone_number excluded from response"""
    return current_user

@router.get("/public/{user_code}", response_model=UserPublicResponse)
def get_public_user_info(
    user_code: str,
    db: Session = Depends(get_db)
):
    """Get minimal public user information by user_code"""
    user = db.query(User).filter(User.user_code == user_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserPublicResponse(
        user_code=user.user_code,
        qr_code_id=user.qr_code_id,
        signup_country_iso=user.signup_country_iso
    )

@router.get("/lookup/{lookup_code}", response_model=UserWithCarsResponse)
def lookup_user(
    lookup_code: str,
    db: Session = Depends(get_db)
):
    """Look up user by user_code or QR code ID for sign-in flow"""
    logger.info(f"User lookup request for identifier: {lookup_code}")
    
    # Check if it's a QR code ID format (starts with QR_)
    if lookup_code.startswith("QR_"):
        user = db.query(User).filter(User.qr_code_id == lookup_code).first()
    else:
        user = db.query(User).filter(User.user_code == lookup_code).first()

    if not user:
        logger.warning(f"User not found for user_code: {lookup_code}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "user_not_found",
                "message": "No account found with this user code"
            }
        )
    
    # Get user's cars
    cars = db.query(Car).filter(Car.owner_id == user.id).all()

    # Convert cars to dict format (excluding license_plate for privacy)
    cars_data = [
        {
            "id": car.id,
            "car_brand": car.car_brand,
            "car_model": car.car_model,
            "created_at": car.created_at.isoformat()
        }
        for car in cars
    ]
    
    # Get user tier (default to 'free' if not set)
    user_tier_value = "free"
    if user.user_tier:
        user_tier_value = user.user_tier.tier

    active_parking_sessions = db.query(ParkingSession).filter(
        ParkingSession.user_id == user.id,
        ParkingSession.end_time.is_(None)
    ).first()

    # Create response (excluding phone_number for privacy)
    response_data = UserWithCarsResponse(
        id=user.id,
        user_code=user.user_code,
        qr_code_id=user.qr_code_id,
        created_at=user.created_at,
        signup_country_iso=user.signup_country_iso,
        qr_image_path=user.qr_image_path,
        profile_deep_link=user.profile_deep_link,
        profile_bio=user.profile_bio,
        profile_display_name=user.profile_display_name,
        user_tier=user_tier_value,
        cars=cars_data,
        parking_status = "active" if active_parking_sessions else "not_parked",
        public_message = active_parking_sessions.public_message if active_parking_sessions else None
    )
    
    logger.info(f"User lookup successful: {user.user_code} with {len(cars_data)} cars")
    return response_data

@router.post("/regenerate-qr", response_model=UserResponse)
def regenerate_user_qr_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate QR code for existing user"""
    logger.info(f"QR code regeneration requested for user_id: {current_user.id}")
    
    old_qr_code = current_user.qr_code_id
    
    # Generate new QR code ID
    qr_code_id = generate_qr_code_id(current_user.user_code, current_user.phone_number)
    
    # Ensure uniqueness
    while db.query(User).filter(User.qr_code_id == qr_code_id).first():
        logger.debug(f"QR code collision during regeneration: {qr_code_id}")
        qr_code_id = generate_qr_code_id(current_user.user_code, current_user.phone_number)
    
    # Update user with new QR code
    current_user.qr_code_id = qr_code_id
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"QR code regenerated: {old_qr_code} -> {qr_code_id}")
    return current_user