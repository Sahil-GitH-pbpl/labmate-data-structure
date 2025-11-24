from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer()


# Mock decode for demo purposes
MOCK_USERS = {
    "alice": {"username": "alice", "role": "Staff", "department": "Operations"},
    "bob": {"username": "bob", "role": "IT", "department": "IT"},
    "admin": {"username": "admin", "role": "Admin", "department": "Admin"},
}


class User:
    def __init__(self, username: str, role: str, department: str):
        self.username = username
        self.role = role
        self.department = department


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    user = MOCK_USERS.get(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return User(**user)


def is_it_or_admin(user: User) -> bool:
    return user.role in {"IT", "Admin"}
