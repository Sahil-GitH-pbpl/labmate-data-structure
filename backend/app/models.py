from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

status_enum = ("New", "Assigned", "In Progress", "On Hold", "Resolved")
category_enum = ("Hardware", "Software", "Office Infra", "Other")


class InfraTicket(Base):
    __tablename__ = "infra_tickets"

    ticket_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_by = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    workstation = Column(String(100), nullable=True)
    status = Column(Enum(*status_enum, name="status_enum"), default="New", nullable=False)
    assigned_to = Column(String(100), nullable=True)
    commitment_time = Column(DateTime(timezone=True), nullable=True)
    is_delayed_pick = Column(Boolean, default=False, nullable=False)
    is_invalid = Column(Boolean, default=False, nullable=False)
    invalid_reason = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    updates = relationship("InfraUpdate", back_populates="ticket", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_created_at", "created_at"),
        Index("idx_department", "department"),
        Index("idx_assigned_to", "assigned_to"),
        Index("idx_delayed", "is_delayed_pick"),
    )


class InfraUpdate(Base):
    __tablename__ = "infra_updates"

    update_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("infra_tickets.ticket_id", ondelete="CASCADE"), nullable=False)
    note = Column(Text, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    ticket = relationship("InfraTicket", back_populates="updates")


__all__ = ["Base", "InfraTicket", "InfraUpdate", "status_enum", "category_enum"]
