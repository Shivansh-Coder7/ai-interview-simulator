from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter()


@router.post("/login", response_model=schemas.TokenResponse)
def admin_login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == data.email).first()
    if not admin or not auth.verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth.create_access_token({"sub": str(admin.id), "role": "admin"})
    return schemas.TokenResponse(access_token=token, user_id=admin.id, name=admin.email)


@router.get("/stats")
def get_stats(
    token_payload: dict = Depends(auth.decode_token),
    db: Session = Depends(get_db),
):
    if token_payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    total_users = db.query(models.User).count()
    total_interviews = db.query(models.InterviewSession).count()
    avg_score = db.query(func.avg(models.InterviewReport.overall_score)).scalar() or 0

    all_roles = [s.job_role for s in db.query(models.InterviewSession).all()]
    most_selected = Counter(all_roles).most_common(5)

    recent = (
        db.query(models.InterviewSession)
        .order_by(models.InterviewSession.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_users": total_users,
        "total_interviews": total_interviews,
        "avg_score": round(avg_score, 1),
        "most_selected_roles": [{"role": r, "count": c} for r, c in most_selected],
        "recent_activity": [
            {
                "session_id": s.id,
                "job_role": s.job_role,
                "interview_type": s.interview_type,
                "status": s.status,
                "created_at": s.created_at.isoformat(),
            }
            for s in recent
        ],
    }
