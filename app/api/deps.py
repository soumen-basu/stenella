from datetime import datetime
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlmodel import Session, select
from app.core import security
from app.core.config import get_settings
from app.db.session import get_session
from app.models.user import User, Session as UserSession

settings = get_settings()

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/api/v1/auth/login" # We will define this endpoint
)

def get_current_user_and_session(
    session: Session = Depends(get_session),
    token: str = Depends(reusable_oauth2)
) -> tuple[User, UserSession]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # We stored session_id in 'sub'? 
        # Plan said: "The JWT payload will contain the session_id (UUID)."
        # In security.py create_access_token, I used "sub": str(subject).
        # I should pass session_id as subject.
        session_id = payload.get("sub")
        if session_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Verify session in DB
    db_session = session.exec(select(UserSession).where(UserSession.id == session_id)).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
        
    # Check expiry of DB session
    if db_session.expires_at < datetime.utcnow():
        # Clean up expired session?
        session.delete(db_session)
        session.commit()
        raise HTTPException(status_code=401, detail="Session expired")

    user = session.get(User, db_session.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user, db_session

def get_current_user(
    current_data: tuple[User, UserSession] = Depends(get_current_user_and_session),
) -> User:
    return current_data[0]

def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
