from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.db.models import FollowupStatus, HiccupStatus, HiccupType, RootCauseCategory


class HiccupCreate(BaseModel):
    hiccup_type: HiccupType
    raised_against: str
    description: str
    immediate_effect: Optional[str] = None
    source_module: Optional[str] = None
    confidential_flag: bool = False


class AutoHiccupRequest(BaseModel):
    source_module: str
    raised_by: str = "System"
    hiccup_type: HiccupType = HiccupType.system
    raised_against: str
    description: str
    immediate_effect: Optional[str] = None
    is_auto_generated: bool = True


class HiccupResponseUpdate(BaseModel):
    response_text: str


class HiccupStatusUpdate(BaseModel):
    status: HiccupStatus
    closure_notes: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    root_cause_category: Optional[RootCauseCategory] = None
    confidential_flag: Optional[bool] = None


class FollowupRequest(BaseModel):
    followup_status: FollowupStatus
    followup_comment: Optional[str] = None


class HiccupResponse(BaseModel):
    hiccup_id: str


class HiccupAuditEntry(BaseModel):
    action: str
    performed_by: int
    remarks: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True


class HiccupDetail(BaseModel):
    hiccup_id: str
    raised_by: int
    raised_by_department: int
    hiccup_type: HiccupType
    raised_against: str
    raised_against_department: Optional[int]
    description: str
    immediate_effect: Optional[str]
    attachment_path: Optional[str]
    response_by: Optional[int]
    response_text: Optional[str]
    status: HiccupStatus
    escalated_by: Optional[int]
    root_cause: Optional[str]
    corrective_action: Optional[str]
    closure_notes: Optional[str]
    closed_at: Optional[datetime]
    is_auto_generated: bool
    source_module: Optional[str]
    confidential_flag: bool
    created_at: datetime
    updated_at: datetime
    root_cause_category: Optional[RootCauseCategory]
    followup_status: FollowupStatus
    followup_comment: Optional[str]
    followup_due: Optional[datetime]
    is_response_overdue: bool = False
    is_closure_overdue: bool = False
    time_since_creation_hours: float = 0
    audit_log: List[HiccupAuditEntry] = []

    class Config:
        orm_mode = True


class HiccupListResponse(BaseModel):
    items: List[HiccupDetail]
    total: int


class TrendSummary(BaseModel):
    key: str
    count: int
    window_days: int = 7


class DigestResponse(BaseModel):
    date: datetime
    raised: int
    responded: int
    closed: int
    escalated: int
    by_department: List[dict]
    sample: List[dict]
