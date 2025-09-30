from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_validator

class MoveRequestCreate(BaseModel):
    '''
    Schema for creating a new move request
    '''
    target_user_code: str
    license_plate: str
    requester_info: Optional[str] = None

    @field_validator('target_user_code')
    def validate_target_user_code(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Target user code cannot be empty")
        return v.strip()

    @field_validator('license_plate')
    def validate_license_plate(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("License Plate cannot be empty")
        if len(v.strip()) > 20:
            raise ValueError("License Plate too long")
        return v.strip().upper()
    
    @field_validator('requester_info')
    def validate_requester_info(cls, v):
        if v and len(v.strip()) > 100:
            raise ValueError("Requester info too long")
        return v.strip() if v else None
    
class MoveRequestResponse(BaseModel):
    '''
    Schema for move request responses
    '''
    id: int
    target_user_code: str
    license_plate: str
    requester_info: Optional[str] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class MoveRequestPreviewItem(BaseModel):
    '''
    Lightweight schema for individual preview items (no redundant fields)
    '''
    id: int
    requester_info: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class MoveRequestPreview(BaseModel):
    '''
    Schema for move request preview response containing list and total count
    '''
    target_user_code: str
    license_plate: str
    requests: List[MoveRequestPreviewItem]
    total_count: int

    model_config = {"from_attributes": True}

class MoveRequestHistoryItem(BaseModel):
    '''
    Schema for individual history items without redundant target_user_code
    '''
    id: int
    license_plate: str
    requester_info: Optional[str] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class MoveRequestHistoryResponse(BaseModel):
    '''
    Schema for move request history response containing list and metadata
    '''
    target_user_code: str
    requests: List[MoveRequestHistoryItem]
    total_count: int
    unread_count: int

    model_config = {"from_attributes": True}

class UnreadCountResponse(BaseModel):
    '''
    Schema for unread count endpoint response
    '''
    unread_count: int

class MarkAsReadRequest(BaseModel):
    '''
    Request schema for marking requests as read
    '''
    request_ids: List[int]

    @field_validator('request_ids')
    def validate_request_ids(cls, v):
        if not v:
            raise ValueError("Request IDs list cannot be empty")
        if len(v) > 100:
            raise ValueError("Too many request IDs (max 100)")
        return v