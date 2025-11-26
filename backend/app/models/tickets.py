from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class FeedbackTicket(Base):
    __tablename__ = "feedback_tickets"

    id = Column(Integer, primary_key=True)
    ticket_number = Column(String(100), unique=True, nullable=False)
    response_id = Column(Integer, ForeignKey("feedback_responses.id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"))
    severity = Column(String(50), default="medium")
    status = Column(String(50), default="open")
    closure_mood = Column(String(50))
    department = Column(String(100))
    summary = Column(String(500))
    details = Column(String(2000))

    response = relationship("FeedbackResponse", back_populates="ticket", foreign_keys=[response_id])
    campaign = relationship("Campaign", back_populates="tickets")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="tickets_created")
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id], back_populates="tickets_assigned")
    updates = relationship("TicketUpdate", back_populates="ticket")


class TicketUpdate(Base):
    __tablename__ = "ticket_updates"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("feedback_tickets.id"), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_by_user_id = Column(Integer, ForeignKey("users.id"))
    update_text = Column(String(2000))
    attachment_path = Column(String(255))
    next_action_due_date = Column(DateTime)

    ticket = relationship("FeedbackTicket", back_populates="updates")
    updated_by_user = relationship("User")
