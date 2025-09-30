from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List

class ChatMessageCreate(BaseModel):
    recipient_user_code: str
    message_content: str
    message_type: str = 'text'
    
    @field_validator('message_type')
    def validate_message_type(cls, v):
        allowed_types = ['text', 'move_car_request']
        if v not in allowed_types:
            raise ValueError(f'Message type must be one of: {allowed_types}')
        return v
    
    @field_validator('message_content')
    def validate_message_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message content cannot be empty')
        if len(v) > 1000:  # Reasonable limit for MVP
            raise ValueError('Message content too long (max 1000 characters)')
        return v.strip()

class ChatMessageResponse(BaseModel):
    id: int
    sender_user_code: str
    recipient_user_code: str
    message_content: str  # This will be decrypted content
    message_type: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class ChatConversationResponse(BaseModel):
    participant_user_code: str
    participant_display_name: Optional[str] = None
    last_message: Optional[ChatMessageResponse] = None
    unread_count: int = 0
    last_activity: datetime

class MarkAsReadRequest(BaseModel):
    message_ids: List[int]

# Pre-defined message for move car requests
MOVE_CAR_REQUEST_MESSAGE = "A verified user has requested you to move your car!"