from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

from app import models
from app.config import get_settings
from app.database import Base, engine
from app.routers import auth, campaigns, dashboard, feedback_public, questionnaire, responses, tickets

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def root(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return RedirectResponse(url="/dashboard", status_code=302)


app.include_router(auth.router, prefix="/auth")
app.include_router(campaigns.router, prefix="/campaigns")
app.include_router(questionnaire.router, prefix="/questionnaire")
app.include_router(feedback_public.router, prefix="/feedback")
app.include_router(responses.router, prefix="/responses")
app.include_router(tickets.router, prefix="/tickets")
app.include_router(dashboard.router, prefix="")
