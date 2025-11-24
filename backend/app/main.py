import os
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .routers import health, tickets, updates
from .services.job_scheduler import shutdown_scheduler, start_scheduler

settings = get_settings()
app = FastAPI(title="Infra HelpDesk", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
static_dir = BASE_DIR.parent / "frontend" / "static"
templates = Jinja2Templates(directory=str(BASE_DIR.parent / "frontend" / "templates"))

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(health.router)
app.include_router(tickets.router)
app.include_router(updates.router)


@app.on_event("startup")
async def startup_event():
    start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    shutdown_scheduler()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/create")
async def create_page(request: Request):
    return templates.TemplateResponse("create_ticket.html", {"request": request})


@app.get("/it-actions")
async def it_actions_page(request: Request):
    return templates.TemplateResponse("it_actions.html", {"request": request})


@app.get("/my-tickets")
async def my_tickets_page(request: Request):
    return templates.TemplateResponse("my_tickets.html", {"request": request})
