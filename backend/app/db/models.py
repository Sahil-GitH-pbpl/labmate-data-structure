import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class RoleEnum(str, enum.Enum):
    staff = "staff"
    management = "management"
    admin = "admin"
    hod = "hod"


class HiccupType(str, enum.Enum):
    person = "Person Related"
    system = "System Related"


class HiccupStatus(str, enum.Enum):
    open = "Open"
    responded = "Responded"
    under_review = "Under Review"
    closed = "Closed"
    escalated = "Escalated to NC"


class RootCauseCategory(str, enum.Enum):
    training = "Training Need"
    process_gap = "Process Gap"
    negligence = "Negligence"
    system_error = "System Error"
    external = "External Factor"
    resource_shortage = "Resource Shortage"


class FollowupStatus(str, enum.Enum):
    pending = "Pending"
    resolved = "Resolved"
    unresolved = "Unresolved"


class DepartmentMaster(Base):
    __tablename__ = "department_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    staff = relationship("StaffMaster", back_populates="department")


class StaffMaster(Base):
    __tablename__ = "staff_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.staff, nullable=False)
    department_id = Column(Integer, ForeignKey("department_master.id"), nullable=True)
    phone = Column(String(30), nullable=True)

    department = relationship("DepartmentMaster", back_populates="staff")


class SystemToken(Base):
    __tablename__ = "system_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)


class Hiccup(Base):
    __tablename__ = "hiccups"

    hiccup_id = Column(String(20), primary_key=True, unique=True)
    raised_by = Column(Integer, ForeignKey("staff_master.id"), nullable=False)
    raised_by_department = Column(Integer, ForeignKey("department_master.id"), nullable=False)
    hiccup_type = Column(Enum(HiccupType), nullable=False)
    raised_against = Column(String(255), nullable=False)
    raised_against_department = Column(Integer, ForeignKey("department_master.id"), nullable=True)
    description = Column(Text, nullable=False)
    immediate_effect = Column(Text, nullable=True)
    attachment_path = Column(String(255), nullable=True)
    response_by = Column(Integer, ForeignKey("staff_master.id"), nullable=True)
    response_text = Column(Text, nullable=True)
    status = Column(Enum(HiccupStatus), nullable=False, default=HiccupStatus.open)
    escalated_by = Column(Integer, ForeignKey("staff_master.id"), nullable=True)
    root_cause = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)
    closure_notes = Column(Text, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    is_auto_generated = Column(Boolean, nullable=False, default=False)
    source_module = Column(String(255), nullable=True)
    confidential_flag = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    root_cause_category = Column(Enum(RootCauseCategory), nullable=True)
    followup_status = Column(Enum(FollowupStatus), nullable=False, default=FollowupStatus.pending)
    followup_comment = Column(Text, nullable=True)
    followup_due = Column(DateTime, nullable=True)

    audit_logs = relationship("HiccupAuditLog", back_populates="hiccup", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_hiccup_status", "status"),
        Index("idx_hiccup_created", "created_at"),
        Index("idx_hiccup_raised_by", "raised_by"),
        Index("idx_hiccup_raised_against", "raised_against"),
        Index("idx_hiccup_source", "source_module"),
    )


class HiccupAuditLog(Base):
    __tablename__ = "hiccup_audit_log"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    hiccup_id = Column(String(20), ForeignKey("hiccups.hiccup_id"), nullable=False)
    action = Column(String(50), nullable=False)
    performed_by = Column(Integer, ForeignKey("staff_master.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    remarks = Column(Text, nullable=True)

    hiccup = relationship("Hiccup", back_populates="audit_logs")


__all__ = [
    "DepartmentMaster",
    "StaffMaster",
    "SystemToken",
    "Hiccup",
    "HiccupAuditLog",
    "HiccupType",
    "HiccupStatus",
    "RootCauseCategory",
    "FollowupStatus",
    "RoleEnum",
]
