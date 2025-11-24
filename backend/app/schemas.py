from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class TicketBase(BaseModel):
    category: str
    subcategory: str
    department: str
    workstation: Optional[str] = None
    description: str


class TicketCreate(TicketBase):
    pass


class TicketSummary(BaseModel):
    ticket_id: int
    category: str
    subcategory: str
    department: str
    description: str
    status: str
    assigned_to: Optional[str] = None
    commitment_time: Optional[datetime] = None
    is_delayed_pick: bool
    is_invalid: bool
    invalid_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TicketListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[TicketSummary]


class PickTicketRequest(BaseModel):
    assigned_to: Optional[str] = None
    commitment_time: datetime

    @validator("commitment_time")
    def commitment_future(cls, value: datetime) -> datetime:
        if value <= datetime.now(tz=value.tzinfo):
            raise ValueError("Commitment time must be in the future")
        return value


class UpdateRequest(BaseModel):
    note: str
    status: Optional[str] = Field(default=None, description="Optional status transition")


class ResolveRequest(BaseModel):
    note: Optional[str] = None


class InvalidRequest(BaseModel):
    invalid_reason: str


class UpdateResponse(BaseModel):
    update_id: int
    ticket_id: int
    note: str
    created_by: str
    created_at: datetime

    class Config:
        orm_mode = True


class UpdatesList(BaseModel):
    ticket_id: int
    updates: List[UpdateResponse]


class HealthResponse(BaseModel):
    status: str = "ok"
