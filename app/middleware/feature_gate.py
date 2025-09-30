from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..models.user import User
from ..models.user_tier import UserTier
from ..dependencies.auth import get_current_user

class FeatureGate:
    """Feature gating utility for premium functionality"""

    @staticmethod
    def check_user_tier(user_code: str, db: Session) -> str:
        """
        Check user's current tier.
        
        Args:
            user_code: 8-character user code
            db: Database session
        
        Returns:
            User tier string ('free' or 'premium')
        
        Raises:
            HTTPException: 404 if user not found
        """
        user = db.query(User).filter(User.user_code == user_code).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_tier = db.query(UserTier).filter(UserTier.user_id == user.id).first()
        if not user_tier:
            user_tier = UserTier(user_id=user.id, tier="free")
            db.add(user_tier)
            db.commit()
        
        return user_tier.tier


    @staticmethod
    def premium_required(func: Callable) -> Callable:
        """
        Decorator to gate premium features.
        
        This decorator checks if the current user has premium access
        before allowing access to the decorated endpoint.
        
        Usage:
            @router.get("/premium-endpoint")
            @FeatureGate.premium_required
            async def premium_function(user: User = Depends(get_current_user)):
                pass
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract dependencies from function signature
            db = None
            user = None

            # Find db session and user from kwargs
            for key, value in kwargs.items():
                if isinstance(value, Session):
                    db = value
                elif isinstance(value, User):
                    user = value
            
            # validate required dependencies
            if not db:
                raise HTTPException(
                    status_code=500,
                    detail="DB session not found in dependencies"
                )
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail= "User authentication required for premium features"
                )
            
            # Check user tier
            user_tier = FeatureGate.check_user_tier(user.user_code, db)
            if user_tier != "premium":
                raise HTTPException(
                    status_code=403,
                    detail="Premium subscription required for this feature"
                )
            
            # User has premium access
            return await func(*args, **kwargs)
        
        return wrapper
    
# Function for FastAPI Depends()
def require_premium():
    """
    Dependency function for premium feature gating.
    
    Usage:
        @router.get("/premium-endpoint")
        async def premium_function(
            _: None = Depends(require_premium),
            user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            pass
    """
    def _check_premium(
            user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
    ):
        user_tier = FeatureGate.check_user_tier(user.user_code, db)
        if user_tier != "premium":
            raise HTTPException(
                status_code=403,
                detail="Premium subscription required for this feature"
            )
        return None
    
    return _check_premium()