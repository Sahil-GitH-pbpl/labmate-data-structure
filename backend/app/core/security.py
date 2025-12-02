from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.schemas import TokenPayload

settings = get_settings()


def create_access_token(user_id: int, name: str, role: str, department_id: Optional[int] = None, expires_minutes: int = 60) -> str:
    to_encode = {
        "sub": user_id,
        "name": name,
        "role": role,
        "department_id": department_id,
        "aud": settings.jwt_audience,
        "iss": settings.jwt_issuer,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
        return TokenPayload(**payload)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
