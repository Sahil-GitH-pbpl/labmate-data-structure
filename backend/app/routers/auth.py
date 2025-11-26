from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.utils import verify_password

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "auth/login.html", {"request": request, "error": "Invalid credentials"}
        )
    request.session["user"] = {"id": user.id, "name": user.name, "role": user.role}
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=302)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(User).get(user_data["id"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(role: Optional[str] = None):
    def _role_dependency(user: User = Depends(get_current_user)):
        if role and user.role != role and user.role != UserRole.admin.value:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return _role_dependency
