import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    display_name: Optional[str] = None
    role: str = Field(default="user")
    is_active: bool = Field(default=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Magic Link fields
    magic_token: Optional[str] = None
    magic_token_expires_at: Optional[datetime] = None

class Session(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: Optional[str] = None # Optional: Store token hash if needed
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic models for API
class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

class UserUpdate(SQLModel):
    display_name: Optional[str] = None
    password: Optional[str] = None
