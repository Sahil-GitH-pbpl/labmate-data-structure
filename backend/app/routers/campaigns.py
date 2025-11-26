from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign, CollectionChannel
from app.routers.auth import get_current_user, require_role

router = APIRouter(tags=["campaigns"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def list_campaigns(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    campaigns = db.query(Campaign).all()
    return templates.TemplateResponse(
        "campaigns/list.html", {"request": request, "campaigns": campaigns, "user": user}
    )


@router.get("/new")
async def new_campaign(request: Request, user=Depends(require_role("admin"))):
    return templates.TemplateResponse(
        "campaigns/edit.html",
        {
            "request": request,
            "campaign": None,
            "action": "/campaigns/new",
            "user": user,
            "channels": [],
        },
    )


@router.post("/new")
async def create_campaign(
    request: Request,
    name: str = Form(...),
    code: str = Form(...),
    campaign_type: str = Form("walk_in"),
    layout_type: str = Form("one_page"),
    primary_language: str = Form("en"),
    estimated_fill_time_seconds: int = Form(60),
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    campaign = Campaign(
        name=name,
        code=code,
        campaign_type=campaign_type,
        layout_type=layout_type,
        primary_language=primary_language,
        estimated_fill_time_seconds=estimated_fill_time_seconds,
        status="draft",
        created_by=user.id,
    )
    db.add(campaign)
    db.commit()
    return RedirectResponse(url="/campaigns/", status_code=302)


@router.get("/{campaign_id}/edit")
async def edit_campaign(
    campaign_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    campaign = db.query(Campaign).get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    channels = db.query(CollectionChannel).all()
    return templates.TemplateResponse(
        "campaigns/edit.html",
        {
            "request": request,
            "campaign": campaign,
            "action": f"/campaigns/{campaign_id}/edit",
            "user": user,
            "channels": channels,
        },
    )


@router.post("/{campaign_id}/edit")
async def update_campaign(
    campaign_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    campaign_type: str = Form("walk_in"),
    status: str = Form("draft"),
    layout_type: str = Form("one_page"),
    primary_language: str = Form("en"),
    estimated_fill_time_seconds: int = Form(60),
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    campaign = db.query(Campaign).get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.name = name
    campaign.description = description
    campaign.campaign_type = campaign_type
    campaign.status = status
    campaign.layout_type = layout_type
    campaign.primary_language = primary_language
    campaign.estimated_fill_time_seconds = estimated_fill_time_seconds
    campaign.updated_at = datetime.utcnow()
    db.commit()
    return RedirectResponse(url="/campaigns/", status_code=302)
