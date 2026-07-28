from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from datetime import datetime
from .database import Base


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255))
    extracted_text = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_role = Column(String(100))
    interview_type = Column(String(50))
    difficulty = Column(String(50))
    qa_log = Column(Text)  # JSON string: [{"question": "...", "answer": "...", "score": ...}, ...]
    status = Column(String(50), default="in_progress")
    created_at = Column(DateTime, default=datetime.utcnow)


class InterviewReport(Base):
    __tablename__ = "interview_reports"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"))
    overall_score = Column(Float)
    technical_score = Column(Float)
    communication_score = Column(Float)
    problem_solving_score = Column(Float)
    confidence_score = Column(Float)
    strengths = Column(Text)
    improvements = Column(Text)
    recommended_topics = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
