"""
SQLAlchemy ORM models for Litigation Simulator backend.
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, Float, Text, JSON, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    organization = Column(String(100))
    role = Column(String(20), default="user")
    created_at = Column(DateTime)
    last_login = Column(DateTime)
    subscription_tier = Column(String(20), default="basic")
    subscription_expires = Column(DateTime)
    is_active = Column(Boolean, default=True)

class Judge(Base):
    __tablename__ = "judges"
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    position = Column(String(100))
    court = Column(String(100))
    court_id = Column(String(36))
    appointed_date = Column(Date)
    birth_year = Column(Integer)
    education = Column(Text)
    prior_positions = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class JudgeAnalytics(Base):
    __tablename__ = "judge_analytics"
    id = Column(Integer, primary_key=True)
    judge_id = Column(String(36), ForeignKey("judges.id"))
    analysis_type = Column(String(50), nullable=False)
    analysis_data = Column(JSON, nullable=False)
    confidence = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Case(Base):
    __tablename__ = "cases"
    id = Column(String(36), primary_key=True)
    case_name = Column(String(255), nullable=False)
    docket_number = Column(String(100))
    court = Column(String(100))
    court_id = Column(String(36))
    date_filed = Column(Date)
    date_terminated = Column(Date)
    nature_of_suit = Column(String(100))
    case_type = Column(String(50))
    judges = Column(JSON)
    status = Column(String(50))
    metadata = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Opinion(Base):
    __tablename__ = "opinions"
    id = Column(String(36), primary_key=True)
    case_id = Column(String(36), ForeignKey("cases.id"))
    author_id = Column(String(36), ForeignKey("judges.id"))
    date_filed = Column(Date)
    type = Column(String(50))
    text = Column(Text)
    text_length = Column(Integer)
    citation = Column(String(255))
    precedential = Column(Boolean)
    citation_count = Column(Integer)
    metadata = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class OralArgument(Base):
    __tablename__ = "oral_arguments"
    id = Column(String(36), primary_key=True)
    case_id = Column(String(36), ForeignKey("cases.id"))
    date_argued = Column(Date)
    duration = Column(Integer)
    panel = Column(JSON)
    transcript = Column(Text)
    audio_url = Column(String(255))
    metadata = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class JudgePattern(Base):
    __tablename__ = "judge_patterns"
    id = Column(Integer, primary_key=True)
    judge_id = Column(String(36), ForeignKey("judges.id"))
    pattern_type = Column(String(50), nullable=False)
    pattern_data = Column(JSON, nullable=False)
    source_count = Column(Integer)
    confidence = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class CasePrediction(Base):
    __tablename__ = "case_predictions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    case_type = Column(String(50), nullable=False)
    case_facts = Column(Text, nullable=False)
    jurisdiction = Column(JSON, nullable=False)
    judge_id = Column(String(36), ForeignKey("judges.id"))
    precedent_strength = Column(Float)
    input_parameters = Column(JSON)
    predicted_outcome = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    class_probabilities = Column(JSON)
    feature_impact = Column(JSON)
    created_at = Column(DateTime)

class SimulationSession(Base):
    __tablename__ = "simulation_sessions"
    id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    case_type = Column(String(50), nullable=False)
    case_facts = Column(Text, nullable=False)
    jurisdiction = Column(JSON, nullable=False)
    judge_id = Column(String(36), ForeignKey("judges.id"))
    rounds_completed = Column(Integer, default=0)
    status = Column(String(20), default="active")
    metrics = Column(JSON)
    feedback = Column(Text)
    created_at = Column(DateTime)
    completed_at = Column(DateTime)

class SimulationQuestion(Base):
    __tablename__ = "simulation_questions"
    id = Column(Integer, primary_key=True)
    simulation_id = Column(String(36), ForeignKey("simulation_sessions.id"))
    question_text = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    source_pattern = Column(String(36))
    round = Column(Integer, nullable=False)
    created_at = Column(DateTime)

class SimulationResponse(Base):
    __tablename__ = "simulation_responses"
    id = Column(Integer, primary_key=True)
    simulation_id = Column(String(36), ForeignKey("simulation_sessions.id"))
    question_id = Column(Integer, ForeignKey("simulation_questions.id"))
    response_text = Column(Text, nullable=False)
    created_at = Column(DateTime)

class SimulationFeedback(Base):
    __tablename__ = "simulation_feedback"
    id = Column(Integer, primary_key=True)
    simulation_id = Column(String(36), ForeignKey("simulation_sessions.id"))
    response_id = Column(Integer, ForeignKey("simulation_responses.id"))
    metrics = Column(JSON, nullable=False)
    feedback_text = Column(Text, nullable=False)
    strengths = Column(JSON)
    improvements = Column(JSON)
    created_at = Column(DateTime)
