from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_management, verify_internal_token
from app.db.models import FollowupStatus, HiccupStatus, HiccupType, StaffMaster, RoleEnum
from app.db.session import get_db
from app.schemas import (
    AutoHiccupRequest,
    FollowupRequest,
    HiccupCreate,
    HiccupDetail,
    HiccupListResponse,
    HiccupResponse,
    HiccupResponseUpdate,
    HiccupStatusUpdate,
)
from app.services.hiccup_service import (
    create_auto_hiccup,
    create_hiccup,
    get_hiccup,
    list_hiccups,
    respond_to_hiccup,
    submit_followup,
    update_status,
)

router = APIRouter(prefix="/hiccups", tags=["hiccups"])


@router.post("", response_model=HiccupResponse)
def raise_hiccup(
    hiccup_type: HiccupType = Form(...),
    raised_against: str = Form(...),
    description: str = Form(...),
    immediate_effect: Optional[str] = Form(None),
    source_module: Optional[str] = Form(None),
    confidential_flag: bool = Form(False),
    attachment: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: StaffMaster = Depends(get_current_user),
):
    payload = HiccupCreate(
        hiccup_type=hiccup_type,
        raised_against=raised_against,
        description=description,
        immediate_effect=immediate_effect,
        source_module=source_module,
        confidential_flag=confidential_flag,
    )
    hiccup = create_hiccup(db, current_user, payload, attachment)
    return HiccupResponse(hiccup_id=hiccup.hiccup_id)


@router.post("/auto_generate", response_model=HiccupResponse, status_code=201)
def auto_generate(
    payload: AutoHiccupRequest,
    db: Session = Depends(get_db),
    _: str = Depends(verify_internal_token),
):
    system_user = db.query(StaffMaster).filter(StaffMaster.id == 1).first()
    if not system_user:
        system_user = StaffMaster(id=1, name="System", role=RoleEnum.admin, department_id=1)
        db.add(system_user)
        db.commit()
        db.refresh(system_user)
    data = HiccupCreate(
        hiccup_type=HiccupType.system,
        raised_against=payload.raised_against,
        description=payload.description,
        immediate_effect=payload.immediate_effect,
        source_module=payload.source_module,
        confidential_flag=False,
    )
    hiccup = create_auto_hiccup(db, data, system_user)
    return HiccupResponse(hiccup_id=hiccup.hiccup_id)


@router.get("", response_model=HiccupListResponse)
def list_my_hiccups(
    status: Optional[HiccupStatus] = None,
    db: Session = Depends(get_db),
    current_user: StaffMaster = Depends(get_current_user),
):
    items = list_hiccups(db, current_user, status)
    return HiccupListResponse(items=items, total=len(items))


@router.get("/{hiccup_id}", response_model=HiccupDetail)
def get_hiccup_detail(
    hiccup_id: str,
    db: Session = Depends(get_db),
    current_user: StaffMaster = Depends(get_current_user),
):
    hiccup = get_hiccup(db, hiccup_id, current_user)
    detail_list = list_hiccups(db, current_user)
    for item in detail_list:
        if item.hiccup_id == hiccup_id:
            return item
    raise ValueError("Hiccup detail missing")


@router.patch("/{hiccup_id}/respond", response_model=HiccupDetail)
def respond(
    hiccup_id: str,
    payload: HiccupResponseUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMaster = Depends(get_current_user),
):
    hiccup = get_hiccup(db, hiccup_id, current_user)
    if hiccup.hiccup_type == HiccupType.person and hiccup.raised_against != str(current_user.id):
        raise HTTPException(status_code=403, detail="Only concerned person may respond")
    if hiccup.hiccup_type == HiccupType.system and current_user.role not in {RoleEnum.management, RoleEnum.admin}:
        raise HTTPException(status_code=403, detail="Management can respond to system issues")
    updated = respond_to_hiccup(db, hiccup, current_user, payload.response_text)
    detail = [h for h in list_hiccups(db, current_user) if h.hiccup_id == updated.hiccup_id][0]
    return detail


@router.patch("/{hiccup_id}/status", response_model=HiccupDetail)
def update_hiccup_status(
    hiccup_id: str,
    payload: HiccupStatusUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMaster = Depends(require_management),
):
    hiccup = get_hiccup(db, hiccup_id, current_user)
    updated = update_status(
        db,
        hiccup,
        current_user,
        payload.status,
        closure_notes=payload.closure_notes,
        root_cause=payload.root_cause,
        corrective_action=payload.corrective_action,
        root_cause_category=payload.root_cause_category,
        confidential_flag=payload.confidential_flag,
    )
    detail = [h for h in list_hiccups(db, current_user) if h.hiccup_id == updated.hiccup_id][0]
    return detail


@router.patch("/{hiccup_id}/followup", response_model=HiccupDetail)
def followup(
    hiccup_id: str,
    payload: FollowupRequest,
    db: Session = Depends(get_db),
    current_user: StaffMaster = Depends(get_current_user),
):
    hiccup = get_hiccup(db, hiccup_id, current_user)
    updated = submit_followup(db, hiccup, current_user, payload.followup_status, payload.followup_comment)
    detail = [h for h in list_hiccups(db, current_user) if h.hiccup_id == updated.hiccup_id][0]
    return detail
