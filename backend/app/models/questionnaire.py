from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.database import Base


class MasterQuestion(Base):
    __tablename__ = "master_questions"

    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True, nullable=False)
    default_text_en = Column(String(1000))
    default_text_hi = Column(String(1000))
    question_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)

    options = relationship("MasterQuestionOption", back_populates="master_question")


class MasterQuestionOption(Base):
    __tablename__ = "master_question_options"

    id = Column(Integer, primary_key=True)
    master_question_id = Column(Integer, ForeignKey("master_questions.id"), nullable=False)
    option_value = Column(String(100), nullable=False)
    option_text_en = Column(String(1000))
    option_text_hi = Column(String(1000))
    sentiment = Column(String(50))
    department = Column(String(100))
    area = Column(String(50))
    score_value = Column(Integer)

    master_question = relationship("MasterQuestion", back_populates="options")


class CampaignQuestion(Base):
    __tablename__ = "campaign_questions"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    master_question_id = Column(Integer, ForeignKey("master_questions.id"))
    question_text_en = Column(String(1000))
    question_text_hi = Column(String(1000))
    question_type = Column(String(50), nullable=False)
    is_required = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    page_number = Column(Integer, default=1)
    is_master = Column(Boolean, default=False)
    is_overall_rating = Column(Boolean, default=False)

    campaign = relationship("Campaign", back_populates="questions")
    master_question = relationship("MasterQuestion")
    options = relationship("CampaignQuestionOption", back_populates="question")
    answers = relationship("FeedbackAnswer", back_populates="question")


class CampaignQuestionOption(Base):
    __tablename__ = "campaign_question_options"

    id = Column(Integer, primary_key=True)
    campaign_question_id = Column(Integer, ForeignKey("campaign_questions.id"), nullable=False)
    option_value = Column(String(100), nullable=False)
    option_text_en = Column(String(1000))
    option_text_hi = Column(String(1000))
    sentiment = Column(String(50))
    department = Column(String(100))
    area = Column(String(50))
    score_value = Column(Integer)

    question = relationship("CampaignQuestion", back_populates="options")


class QuestionFlowRule(Base):
    __tablename__ = "question_flow_rules"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    source_question_id = Column(Integer, ForeignKey("campaign_questions.id"))
    source_option_value = Column(String(100))
    target_question_id = Column(Integer, ForeignKey("campaign_questions.id"))
    condition_type = Column(String(50), default="equals")

    campaign = relationship("Campaign")
