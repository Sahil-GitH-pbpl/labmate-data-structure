from fastapi import APIRouter

from app.core.security import create_access_token
from app.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def issue_token(data: LoginRequest):
    token = create_access_token(user_id=data.user_id, name=data.name, role=data.role.value, department_id=data.department_id)
    return TokenResponse(access_token=token)
