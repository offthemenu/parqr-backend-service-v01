from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User
from app.schemas.user_schema import UserRegisterRequest, UserResponse, UserPublicResponse
from app.dependencies.auth import get_current_user
import secrets
import string
import hashlib
import uuid
import logging
import sys
from pathlib import Path

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from country_codes import get_servicing_countries_list, is_valid_country_iso

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v01/signup", tags=["signup"])

@router.get("/servicing-countries")
def get_servicing_countries():
    """Get list of countries that parQR services for signup dropdown"""
    logger.info("Servicing countries list requested")
    
    try:
        countries = get_servicing_countries_list()
        logger.info(f"Returning {len(countries)} servicing countries")
        return {"countries": countries}
    except Exception as e:
        logger.error(f"Error fetching servicing countries: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve servicing countries")