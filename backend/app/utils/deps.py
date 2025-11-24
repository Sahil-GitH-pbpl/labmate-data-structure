from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth.arpra_jwt import User, get_current_user, is_it_or_admin
from ..db import get_db


def get_db_session():
    with get_db() as db:
        yield db


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    return user


def get_it_admin_user(user: User = Depends(get_current_user)) -> User:
    if not is_it_or_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return user
