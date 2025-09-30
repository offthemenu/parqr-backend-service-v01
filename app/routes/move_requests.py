from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
import logging

from app.db.base import get_db
from app.models.move_request import MoveRequest
from app.models.user import User
from app.schemas.move_request_schema import (
    MoveRequestCreate,
    MoveRequestResponse,
    MoveRequestPreviewItem,
    MoveRequestPreview,
    MoveRequestHistoryItem,
    MoveRequestHistoryResponse,
    UnreadCountResponse,
    MarkAsReadRequest
)
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/v01/move_requests", tags=["move_requests"])

@router.get("/unread_count/{user_code}", response_model=UnreadCountResponse)
async def get_unread_move_requests_count(
    user_code: str,
    db: Session = Depends(get_db)
) -> UnreadCountResponse:
    '''
    Get count of totla unread move requests for notification badging

    Used by the HomeScreen to display the notification badge showing how many unread move requests the user has received

    Args:
        user_code: user code (8 characters)
        db: Database session

    Returns:
        UnreadCountResponse with unread_count field

    Raises:
        HTTPException: 404 if user not found
    '''

    # User verification
    user = db.query(User).filter(User.user_code == user_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Count unread move requests for this user
    unread_count = db.query(MoveRequest).filter(
        and_(
            MoveRequest.target_user_id == user.id,
            MoveRequest.is_read == False
        )
    ).count()

    return UnreadCountResponse(unread_count=unread_count)

@router.get("/preview/{user_code}", response_model=MoveRequestPreview)
async def get_move_requests_preview(
    user_code: str,
    limit: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
) -> MoveRequestPreview:
    '''
    Get preview list of recent mvoe requests for HomeScreen display.

    This endpoint returns a limited list of the most recent move reqeusts for display in the HomeScreen's ParkOutRequests section

    Args:
        user_code: user code (8 characters)
        limit: Number of requests to return (1-10, default to 3)
        db: Database session
    
    Returns:
        MoveRequestPreview with requests list and total_count

    Raises:
        HTTPException: 404 if user not found
    '''
    # User verification
    user = db.query(User).filter(User.user_code == user_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get total count of all requests for this user
    total_count = db.query(MoveRequest).filter(
        MoveRequest.target_user_id ==  user.id
    ).count()

    # Get limited preview of most recent requests
    recent_requests = db.query(MoveRequest).filter(
        MoveRequest.target_user_id == user.id
    ).order_by(desc(MoveRequest.created_at)).limit(limit).all()

    # Get license plate from the most recent requests
    license_plate = recent_requests[0].license_plate if recent_requests else ""

    return MoveRequestPreview(
        target_user_code=user.user_code,
        license_plate=license_plate,
        requests=[MoveRequestPreviewItem.from_attributes(req) for req in recent_requests],
        total_count=total_count
    )

@router.post("/create", response_model=MoveRequestResponse)
async def create_move_request(
    request: MoveRequestCreate,
    client_request: Request,
    db: Session = Depends(get_db)
) -> MoveRequestResponse:
    '''
    Create new anonymous park-out request.
    
    This endpoint allows anyone to create a move request for a parked car
    by providing the target user's code and license plate. No authentication
    required as this supports anonymous reporting.
    
    Args:
        request: Move request creation data
        client_request: FastAPI request object for IP extraction
        db: Database session
    
    Returns:
        MoveRequestResponse with created request details
    
    Raises:
        HTTPException: 404 if target user not found
        HTTPException: 422 if validation fails
    '''
    # User verification
    target_user = db.query(User).filter(User.user_code == request.target_user_code).first()
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User with code {request.target_user_code} not found")
    
    # IP Address from the request
    client_ip = client_request.client.host
    if hasattr(client_request.headers, "x-forwarded-for"):
        # handle proxy/load balancing forwarded IP
        forwarded_ips = client_request.headers.get('x-forwarded-for', '').split(",")
        client_ip = forwarded_ips[0].strip() or client_ip
    
    # Create new move request (ParkOut)
    db_request = MoveRequest(
        target_user_id = target_user.id,
        license_plate = request.license_plate,
        requester_info = request.requester_info,
        ip_address = client_ip,
        is_read = False # New requests default to False
    )

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return MoveRequestResponse.model_validate(db_request)

@router.put("/{request_id}/mark_read", response_model= dict)
async def mark_move_reqeust_as_read(
    request_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Mark a move request as read.
    
    This endpoint is called when the user views a move request to update
    its read status and remove it from the unread count.
    
    Args:
        request_id: ID of the move request to mark as read
        db: Database session
    
    Returns:
        Success confirmation message
    
    Raises:
        HTTPException: 404 if request not found
    """
    # Find the move request
    move_request = db.query(MoveRequest).filter(MoveRequest.id == request_id).first()
    if not move_request:
        raise HTTPException(status_code=404, detail="Move request not found")
    
    # Mark as read with current timestamp
    move_request.is_read = True
    move_request.viewed_at = func.now()

    db.commit()

    return {"message": f"Move request {request_id} marked as read"}

@router.get("/history/{user_code}", response_model=MoveRequestHistoryResponse)
async def get_move_request_history(
    user_code: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db)
) -> MoveRequestHistoryResponse:
    """
    Get full move request history for user.
    
    This endpoint provides paginated access to all move requests received
    by a user, with optional filtering for unread requests only.
    
    Args:
        user_code: 8-character user code
        limit: Number of requests to return (1-200, default 50)
        offset: Number of requests to skip (default 0)
        unread_only: If True, only return unread requests
        db: Database session
    
    Returns:
        MoveRequestHistoryResponse with user info, requests list, and counts
    
    Raises:
        HTTPException: 404 if user not found
    """
    # User verification
    user = db.query(User).filter(User.user_code == user_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Optional unread filter
    if unread_only == False:
        query = db.query(MoveRequest).filter(MoveRequest.target_user_id == user.id)
    elif unread_only == True:
        query = db.query(MoveRequest).filter(
            and_(
                MoveRequest.target_user_id == user.id,
                MoveRequest.is_read == False
            )
        )
    
    # Get total counts
    total_count = query.count()
    unread_count = db.query(MoveRequest).filter(
            and_(
                MoveRequest.target_user_id == user.id,
                MoveRequest.is_read == False
            )
        ).count()

    # Apply pagination and ordering
    requests = query.order_by(desc(MoveRequest.created_at)).offset(offset).limit(limit).all()

    return MoveRequestHistoryResponse(
        target_user_code=user.user_code,
        requests=[MoveRequestHistoryItem.from_attributes(req) for req in requests],
        total_count=total_count,
        unread_count=unread_count
    )
