from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(String(1000))
    campaign_type = Column(String(100))
    status = Column(String(50), default="draft")
    primary_language = Column(String(10), default="en")
    available_languages = Column(JSON, default=["en"])
    layout_type = Column(String(50), default="one_page")
    estimated_fill_time_seconds = Column(Integer, default=60)
    start_date = Column(Date)
    end_date = Column(Date)
    is_forever = Column(Boolean, default=True)
    max_score = Column(Integer)
    scoring_method = Column(String(50), default="simple_avg")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    channels = relationship("CampaignChannel", back_populates="campaign")
    pii_fields = relationship("CampaignPiiField", back_populates="campaign")
    questions = relationship("CampaignQuestion", back_populates="campaign")
    recipient_lists = relationship("CampaignRecipientList", back_populates="campaign")
    send_schedules = relationship("CampaignSendSchedule", back_populates="campaign")
    responses = relationship("FeedbackResponse", back_populates="campaign")
    tickets = relationship("FeedbackTicket", back_populates="campaign")


class CampaignChannel(Base):
    __tablename__ = "campaign_channels"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("collection_channels.id"), nullable=False)
    config = Column(JSON)

    campaign = relationship("Campaign", back_populates="channels")
    channel = relationship("CollectionChannel", back_populates="campaign_channels")


class PiiField(Base):
    __tablename__ = "pii_fields"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    field_type = Column(String(50), nullable=False)
    is_required = Column(Boolean, default=False)

    campaign_links = relationship("CampaignPiiField", back_populates="pii_field")


class CampaignPiiField(Base):
    __tablename__ = "campaign_pii_fields"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    pii_field_id = Column(Integer, ForeignKey("pii_fields.id"), nullable=False)
    is_required = Column(Boolean, default=False)
    prefill_source = Column(String(100), default="manual_entry")
    display_label = Column(String(255))

    campaign = relationship("Campaign", back_populates="pii_fields")
    pii_field = relationship("PiiField", back_populates="campaign_links")


class CampaignRecipientList(Base):
    __tablename__ = "campaign_recipient_lists"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    source_type = Column(String(100), default="upload_csv")
    name = Column(String(255), nullable=False)
    description = Column(String(500))

    campaign = relationship("Campaign", back_populates="recipient_lists")
    recipients = relationship("CampaignRecipient", back_populates="recipient_list")


class CampaignRecipient(Base):
    __tablename__ = "campaign_recipients"

    id = Column(Integer, primary_key=True)
    recipient_list_id = Column(Integer, ForeignKey("campaign_recipient_lists.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    pii_data_json = Column(JSON)
    personalized_link_token = Column(String(100), unique=True)
    status = Column(String(50), default="pending")

    recipient_list = relationship("CampaignRecipientList", back_populates="recipients")
    campaign = relationship("Campaign")
    responses = relationship("FeedbackResponse", back_populates="recipient")


class CampaignSendSchedule(Base):
    __tablename__ = "campaign_send_schedules"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    trigger_type = Column(String(50), default="event")
    offset_minutes = Column(Integer, default=0)
    channel_id = Column(Integer, ForeignKey("collection_channels.id"))
    is_active = Column(Boolean, default=True)

    campaign = relationship("Campaign", back_populates="send_schedules")
    channel = relationship("CollectionChannel")
