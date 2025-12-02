from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import RoleEnum


class User(BaseModel):
    id: int
    name: str
    role: RoleEnum
    department_id: Optional[int] = None
    phone: Optional[str] = None

    class Config:
        orm_mode = True


class TokenPayload(BaseModel):
    sub: int
    name: str
    role: RoleEnum
    department_id: Optional[int] = None
    exp: Optional[int] = None
    aud: Optional[str] = None
    iss: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    user_id: int
    name: str
    role: RoleEnum
    department_id: Optional[int] = None
    phone: Optional[str] = None
