from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, Enum):
    l1 = "l1"
    l2 = "l2"
    l3 = "l3"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    mobile = Column(String(50))
    role = Column(String(20), nullable=False, default=UserRole.l1.value)
    department = Column(String(100))
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    tickets_created = relationship(
        "FeedbackTicket", back_populates="created_by_user", foreign_keys="FeedbackTicket.created_by"
    )
    tickets_assigned = relationship(
        "FeedbackTicket", back_populates="assigned_to", foreign_keys="FeedbackTicket.assigned_to_user_id"
    )


class CollectionChannel(Base):
    __tablename__ = "collection_channels"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    campaign_channels = relationship("CampaignChannel", back_populates="channel")


class FeedbackActionType(Base):
    __tablename__ = "feedback_action_types"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))


class FeedbackReward(Base):
    __tablename__ = "feedback_rewards"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    criteria_json = Column(String(1000))
    is_active = Column(Boolean, default=True)

    response_rewards = relationship("ResponseReward", back_populates="reward")
