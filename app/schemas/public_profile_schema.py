from typing import Optional, Dict, Any
from pydantic import BaseModel

class PublicProfileResponse(BaseModel):
    '''
    Public profile data for QR scanning workflow
    '''

    user_code: str
    display_name: Optional[str] = None
    bio: Optional[str] = None

    # Car Information (if actively connected to the account)
    active_car: Optional[Dict[str, Any]] = None

    # Current Parking status
    parking_status: Dict[str, Any]

    # Public message (if any)
    public_message: Optional[str] = None

    model_config = {"from_attributes": True}