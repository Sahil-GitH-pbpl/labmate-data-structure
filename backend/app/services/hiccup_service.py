import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.models import (
    FollowupStatus,
    Hiccup,
    HiccupAuditLog,
    HiccupStatus,
    HiccupType,
    RootCauseCategory,
    StaffMaster,
    RoleEnum,
)
from app.schemas import HiccupCreate, HiccupDetail, HiccupAuditEntry
from app.utils.id_generator import generate_hiccup_id
from app.core.config import get_settings
from app.integrations.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)
settings = get_settings()


ALLOWED_ATTACHMENT_TYPES = {"application/pdf", "image/png", "image/jpeg"}
MAX_FILE_SIZE_MB = 10


def save_attachment(hiccup_id: str, upload: UploadFile | None) -> Optional[str]:
    if not upload:
        return None
    if upload.content_type not in ALLOWED_ATTACHMENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    upload.file.seek(0, 2)
    size_mb = upload.file.tell() / (1024 * 1024)
    upload.file.seek(0)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="Attachment too large")
    target_dir = settings.upload_dir.rstrip("/") + f"/{hiccup_id}"
    import os

    os.makedirs(target_dir, exist_ok=True)
    target_path = f"{target_dir}/{upload.filename}"
    with open(target_path, "wb") as f:
        f.write(upload.file.read())
    return target_path


def add_audit_log(db: Session, hiccup_id: str, action: str, performed_by: int, remarks: Optional[str] = None) -> None:
    log_entry = HiccupAuditLog(hiccup_id=hiccup_id, action=action, performed_by=performed_by, remarks=remarks)
    db.add(log_entry)


def build_notification_message(hiccup: Hiccup, raised_by: StaffMaster) -> str:
    desc = hiccup.description[:120]
    return (
        "⚠️ New Hiccup Raised!\n"
        f"ID: {hiccup.hiccup_id}\n"
        f"Raised By: {raised_by.name}\n"
        f"Type: {hiccup.hiccup_type.value}\n"
        f"Time: {hiccup.created_at}\n"
        f"Summary: {desc}"
    )


def create_hiccup(db: Session, user: StaffMaster, data: HiccupCreate, attachment: UploadFile | None = None) -> Hiccup:
    hiccup_id = generate_hiccup_id(db)
    attachment_path = save_attachment(hiccup_id, attachment)
    raised_against_department = None
    if data.hiccup_type == HiccupType.person:
        try:
            target_id = int(data.raised_against)
        except ValueError:
            raise HTTPException(status_code=400, detail="raised_against must be staff id for person related")
        target_staff = db.query(StaffMaster).filter(StaffMaster.id == target_id).first()
        if target_staff:
            raised_against_department = target_staff.department_id
    hiccup = Hiccup(
        hiccup_id=hiccup_id,
        raised_by=user.id,
        raised_by_department=user.department_id or 1,
        hiccup_type=data.hiccup_type,
        raised_against=data.raised_against,
        raised_against_department=raised_against_department,
        description=data.description,
        immediate_effect=data.immediate_effect,
        attachment_path=attachment_path,
        status=HiccupStatus.open,
        is_auto_generated=False,
        source_module=data.source_module,
        confidential_flag=data.confidential_flag,
        followup_status=FollowupStatus.pending,
    )
    db.add(hiccup)
    add_audit_log(db, hiccup_id, "Created", user.id)
    db.commit()
    db.refresh(hiccup)

    message = build_notification_message(hiccup, user)
    recipients: List[str]
    if hiccup.hiccup_type == HiccupType.person:
        recipients = [target_staff.phone] if target_staff and target_staff.phone else []
    else:
        recipients = settings.management_numbers
    send_whatsapp_message(recipients, message)
    return hiccup


def create_auto_hiccup(db: Session, data: HiccupCreate, system_user: StaffMaster) -> Hiccup:
    hiccup_id = generate_hiccup_id(db)
    hiccup = Hiccup(
        hiccup_id=hiccup_id,
        raised_by=system_user.id,
        raised_by_department=system_user.department_id or 1,
        hiccup_type=HiccupType.system,
        raised_against=data.raised_against,
        description=data.description,
        immediate_effect=data.immediate_effect,
        status=HiccupStatus.open,
        is_auto_generated=True,
        source_module=data.source_module,
        confidential_flag=False,
        followup_status=FollowupStatus.pending,
    )
    db.add(hiccup)
    add_audit_log(db, hiccup_id, "Created", system_user.id)
    db.commit()
    db.refresh(hiccup)
    send_whatsapp_message(settings.management_numbers, build_notification_message(hiccup, system_user))
    return hiccup


def respond_to_hiccup(db: Session, hiccup: Hiccup, responder: StaffMaster, response_text: str) -> Hiccup:
    hiccup.response_by = responder.id
    hiccup.response_text = response_text
    hiccup.status = HiccupStatus.responded
    hiccup.updated_at = datetime.utcnow()
    add_audit_log(db, hiccup.hiccup_id, "Responded", responder.id)
    db.commit()
    db.refresh(hiccup)
    return hiccup


def update_status(
    db: Session,
    hiccup: Hiccup,
    actor: StaffMaster,
    status: HiccupStatus,
    closure_notes: Optional[str] = None,
    root_cause: Optional[str] = None,
    corrective_action: Optional[str] = None,
    root_cause_category: Optional[RootCauseCategory] = None,
    confidential_flag: Optional[bool] = None,
) -> Hiccup:
    if status == HiccupStatus.closed and not closure_notes:
        raise HTTPException(status_code=400, detail="Closure notes required")
    if status == HiccupStatus.escalated and (not root_cause or not corrective_action):
        raise HTTPException(status_code=400, detail="Root cause and corrective action required to escalate")

    hiccup.status = status
    hiccup.closure_notes = closure_notes or hiccup.closure_notes
    hiccup.root_cause = root_cause or hiccup.root_cause
    hiccup.corrective_action = corrective_action or hiccup.corrective_action
    hiccup.root_cause_category = root_cause_category or hiccup.root_cause_category
    if confidential_flag is not None:
        hiccup.confidential_flag = confidential_flag
    if status in {HiccupStatus.closed, HiccupStatus.escalated}:
        hiccup.closed_at = datetime.utcnow()
        hiccup.followup_due = datetime.utcnow() + timedelta(days=7)
        hiccup.followup_status = FollowupStatus.pending
    if status == HiccupStatus.escalated:
        hiccup.escalated_by = actor.id
    hiccup.updated_at = datetime.utcnow()
    add_audit_log(db, hiccup.hiccup_id, "StatusChanged", actor.id, remarks=status.value)
    db.commit()
    db.refresh(hiccup)
    return hiccup


def apply_rbac_filters(db: Session, user: StaffMaster):
    query = db.query(Hiccup)
    if user.role in {RoleEnum.management, RoleEnum.admin}:
        return query
    if user.role == RoleEnum.hod:
        return query.filter(
            (Hiccup.raised_by_department == user.department_id)
            | (Hiccup.raised_against_department == user.department_id)
        )
    else:
        return query.filter(
            (Hiccup.raised_by == user.id)
            | (Hiccup.raised_against == str(user.id))
        )


def is_confidential_allowed(hiccup: Hiccup, user: StaffMaster) -> bool:
    if not hiccup.confidential_flag:
        return True
    return user.role in {RoleEnum.management, RoleEnum.admin} or hiccup.raised_by == user.id


def compute_flags(hiccup: Hiccup) -> dict:
    now = datetime.utcnow()
    response_overdue = False
    closure_overdue = False
    if hiccup.status == HiccupStatus.open and now - hiccup.created_at > timedelta(hours=24):
        response_overdue = True
    if hiccup.status == HiccupStatus.responded and now - hiccup.updated_at > timedelta(hours=72):
        closure_overdue = True
    time_since = (now - hiccup.created_at).total_seconds() / 3600
    return {"is_response_overdue": response_overdue, "is_closure_overdue": closure_overdue, "time_since_creation_hours": time_since}


def list_hiccups(db: Session, user: StaffMaster, status: Optional[HiccupStatus] = None) -> List[HiccupDetail]:
    query = apply_rbac_filters(db, user)
    if status:
        query = query.filter(Hiccup.status == status)
    records = query.order_by(Hiccup.created_at.desc()).all()
    visible = [h for h in records if is_confidential_allowed(h, user)]
    result: List[HiccupDetail] = []
    for hiccup in visible:
        flags = compute_flags(hiccup)
        audit_entries = [
            HiccupAuditEntry(
                action=log.action, performed_by=log.performed_by, remarks=log.remarks, timestamp=log.timestamp
            )
            for log in hiccup.audit_logs
        ]
        result.append(
            HiccupDetail(
                hiccup_id=hiccup.hiccup_id,
                raised_by=hiccup.raised_by,
                raised_by_department=hiccup.raised_by_department,
                hiccup_type=hiccup.hiccup_type,
                raised_against=hiccup.raised_against,
                raised_against_department=hiccup.raised_against_department,
                description=hiccup.description,
                immediate_effect=hiccup.immediate_effect,
                attachment_path=hiccup.attachment_path,
                response_by=hiccup.response_by,
                response_text=hiccup.response_text,
                status=hiccup.status,
                escalated_by=hiccup.escalated_by,
                root_cause=hiccup.root_cause,
                corrective_action=hiccup.corrective_action,
                closure_notes=hiccup.closure_notes,
                closed_at=hiccup.closed_at,
                is_auto_generated=hiccup.is_auto_generated,
                source_module=hiccup.source_module,
                confidential_flag=hiccup.confidential_flag,
                created_at=hiccup.created_at,
                updated_at=hiccup.updated_at,
                root_cause_category=hiccup.root_cause_category,
                followup_status=hiccup.followup_status,
                followup_comment=hiccup.followup_comment,
                followup_due=hiccup.followup_due,
                audit_log=audit_entries,
                **flags,
            )
        )
    return result


def get_hiccup(db: Session, hiccup_id: str, user: StaffMaster) -> Hiccup:
    hiccup = db.query(Hiccup).filter(Hiccup.hiccup_id == hiccup_id).first()
    if not hiccup:
        raise HTTPException(status_code=404, detail="Hiccup not found")
    if not is_confidential_allowed(hiccup, user):
        raise HTTPException(status_code=403, detail="Not authorized to view this hiccup")
    return hiccup


def submit_followup(db: Session, hiccup: Hiccup, user: StaffMaster, status: FollowupStatus, comment: Optional[str]) -> Hiccup:
    if hiccup.raised_by != user.id:
        raise HTTPException(status_code=403, detail="Only raiser can submit followup")
    hiccup.followup_status = status
    hiccup.followup_comment = comment
    hiccup.updated_at = datetime.utcnow()
    add_audit_log(db, hiccup.hiccup_id, "Followup", user.id, remarks=status.value)
    db.commit()
    db.refresh(hiccup)
    return hiccup
