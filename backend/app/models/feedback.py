from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.database import Base


class FeedbackResponse(Base):
    __tablename__ = "feedback_responses"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("campaign_recipients.id"))
    submission_time = Column(DateTime, default=datetime.utcnow)
    language = Column(String(10), default="en")
    overall_score = Column(Integer)
    overall_sentiment = Column(String(50))
    overall_rating_value = Column(Integer)
    needs_manual_review = Column(Boolean, default=False)
    is_complaint = Column(Boolean, default=False)
    ticket_id = Column(Integer, ForeignKey("feedback_tickets.id"))
    status = Column(String(50), default="auto_processed")
    pii_data_json = Column(JSON)

    campaign = relationship("Campaign", back_populates="responses")
    recipient = relationship("CampaignRecipient", back_populates="responses")
    answers = relationship("FeedbackAnswer", back_populates="response")
    files = relationship("FeedbackFile", back_populates="response")
    ticket = relationship("FeedbackTicket", back_populates="response", foreign_keys=[ticket_id])
    rewards = relationship("ResponseReward", back_populates="response")


class FeedbackAnswer(Base):
    __tablename__ = "feedback_answers"

    id = Column(Integer, primary_key=True)
    response_id = Column(Integer, ForeignKey("feedback_responses.id"), nullable=False)
    campaign_question_id = Column(Integer, ForeignKey("campaign_questions.id"), nullable=False)
    answer_text = Column(String(2000))
    selected_option_values = Column(JSON)
    sentiment = Column(String(50))
    department = Column(String(100))
    area = Column(String(50))
    score_value = Column(Integer)

    response = relationship("FeedbackResponse", back_populates="answers")
    question = relationship("CampaignQuestion", back_populates="answers")


class FeedbackFile(Base):
    __tablename__ = "feedback_files"

    id = Column(Integer, primary_key=True)
    response_id = Column(Integer, ForeignKey("feedback_responses.id"), nullable=False)
    campaign_question_id = Column(Integer, ForeignKey("campaign_questions.id"))
    file_path = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    response = relationship("FeedbackResponse", back_populates="files")


class ResponseReward(Base):
    __tablename__ = "response_rewards"

    id = Column(Integer, primary_key=True)
    response_id = Column(Integer, ForeignKey("feedback_responses.id"), nullable=False)
    reward_id = Column(Integer, ForeignKey("feedback_rewards.id"), nullable=False)
    status = Column(String(50), default="pending")

    response = relationship("FeedbackResponse", back_populates="rewards")
    reward = relationship("FeedbackReward", back_populates="response_rewards")
