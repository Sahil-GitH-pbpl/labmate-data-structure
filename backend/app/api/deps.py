from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.models import RoleEnum, StaffMaster, SystemToken
from app.db.session import get_db


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> StaffMaster:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    user = db.query(StaffMaster).filter(StaffMaster.id == payload.sub).first()
    if not user:
        user = StaffMaster(id=payload.sub, name=payload.name, role=payload.role, department_id=payload.department_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def require_management(user: StaffMaster = Depends(get_current_user)) -> StaffMaster:
    if user.role not in {RoleEnum.management, RoleEnum.admin}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Management access required")
    return user


def require_admin(user: StaffMaster = Depends(get_current_user)) -> StaffMaster:
    if user.role != RoleEnum.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def verify_internal_token(x_internal_token: str = Header(None), db: Session = Depends(get_db)) -> str:
    if not x_internal_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing internal token")
    token_row = db.query(SystemToken).filter(SystemToken.token == x_internal_token, SystemToken.active.is_(True)).first()
    if not token_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token")
    return x_internal_token
