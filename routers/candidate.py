from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from .. import models, schemas, auth
from ..resume import extract_resume_text

router = APIRouter()


@router.post("/signup", response_model=schemas.TokenResponse)
def signup(data: schemas.UserSignup, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        name=data.name,
        email=data.email,
        password_hash=auth.hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id), "role": "candidate"})
    return schemas.TokenResponse(access_token=token, user_id=user.id, name=user.name)


@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth.create_access_token({"sub": str(user.id), "role": "candidate"})
    return schemas.TokenResponse(access_token=token, user_id=user.id, name=user.name)


@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    token_payload: dict = Depends(auth.decode_token),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    text = extract_resume_text(file_bytes)

    resume = models.Resume(
        user_id=int(token_payload["sub"]),
        filename=file.filename,
        extracted_text=text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {"resume_id": resume.id, "filename": resume.filename}


@router.get("/dashboard")
def candidate_dashboard(
    token_payload: dict = Depends(auth.decode_token),
    db: Session = Depends(get_db),
):
    user_id = int(token_payload["sub"])
    user = db.query(models.User).filter(models.User.id == user_id).first()

    latest_resume = (
        db.query(models.Resume)
        .filter(models.Resume.user_id == user_id)
        .order_by(models.Resume.uploaded_at.desc())
        .first()
    )

    sessions = (
        db.query(models.InterviewSession)
        .filter(models.InterviewSession.user_id == user_id)
        .order_by(models.InterviewSession.created_at.desc())
        .all()
    )

    reports = []
    for s in sessions:
        report = (
            db.query(models.InterviewReport)
            .filter(models.InterviewReport.session_id == s.id)
            .first()
        )
        reports.append({
            "session_id": s.id,
            "job_role": s.job_role,
            "status": s.status,
            "overall_score": report.overall_score if report else None,
        })

    return {
        "name": user.name,
        "email": user.email,
        "resume_uploaded": latest_resume is not None,
        "interviews_completed": len([s for s in sessions if s.status == "completed"]),
        "latest_score": reports[0]["overall_score"] if reports else None,
        "reports": reports,
    }
