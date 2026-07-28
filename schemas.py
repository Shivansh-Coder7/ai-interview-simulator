from pydantic import BaseModel, EmailStr
from typing import Optional


class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: Optional[str] = None


class StartInterviewRequest(BaseModel):
    resume_id: int
    job_role: str
    interview_type: str  # Technical / HR / Mixed
    difficulty: str      # Easy / Medium / Hard


class AnswerRequest(BaseModel):
    session_id: int
    answer: str


class QuestionResponse(BaseModel):
    session_id: int
    question: Optional[str] = None
    finished: bool = False


class ReportResponse(BaseModel):
    overall_score: float
    technical_score: float
    communication_score: float
    problem_solving_score: float
    confidence_score: float
    strengths: str
    improvements: str
    recommended_topics: str
