import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, auth, ai

router = APIRouter()

MAX_QUESTIONS = 7  # fixed length keeps report generation predictable and demo-able


@router.post("/start", response_model=schemas.QuestionResponse)
def start_interview(
    data: schemas.StartInterviewRequest,
    token_payload: dict = Depends(auth.decode_token),
    db: Session = Depends(get_db),
):
    user_id = int(token_payload["sub"])
    resume = db.query(models.Resume).filter(models.Resume.id == data.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    session = models.InterviewSession(
        user_id=user_id,
        resume_id=data.resume_id,
        job_role=data.job_role,
        interview_type=data.interview_type,
        difficulty=data.difficulty,
        qa_log=json.dumps([]),
        status="in_progress",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    question = ai.generate_question(
        resume.extracted_text, data.job_role, data.difficulty, data.interview_type, []
    )

    # store this first question as "pending" (no answer yet) so /answer can find it
    session.qa_log = json.dumps([{"question": question}])
    db.commit()

    return schemas.QuestionResponse(session_id=session.id, question=question, finished=False)


@router.post("/answer", response_model=schemas.QuestionResponse)
def submit_answer(
    data: schemas.AnswerRequest,
    token_payload: dict = Depends(auth.decode_token),
    db: Session = Depends(get_db),
):
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == data.session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    qa_log = json.loads(session.qa_log)
    resume = db.query(models.Resume).filter(models.Resume.id == session.resume_id).first()

    # Determine the question being answered: the most recently asked, unanswered one
    if qa_log and "answer" not in qa_log[-1]:
        qa_log[-1]["answer"] = data.answer
        qa_log[-1]["score"] = ai.evaluate_answer(qa_log[-1]["question"], data.answer)
    else:
        # Shouldn't normally happen, but guard against a stray call
        raise HTTPException(status_code=400, detail="No pending question for this session")

    session.qa_log = json.dumps(qa_log)
    db.commit()

    if len(qa_log) >= MAX_QUESTIONS:
        session.status = "completed"
        db.commit()
        return schemas.QuestionResponse(session_id=session.id, question=None, finished=True)

    next_question = ai.generate_question(
        resume.extracted_text, session.job_role, session.difficulty,
        session.interview_type, qa_log,
    )
    qa_log.append({"question": next_question})
    session.qa_log = json.dumps(qa_log)
    db.commit()

    return schemas.QuestionResponse(session_id=session.id, question=next_question, finished=False)


@router.post("/finish", response_model=schemas.ReportResponse)
def finish_interview(
    session_id: int,
    token_payload: dict = Depends(auth.decode_token),
    db: Session = Depends(get_db),
):
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    qa_log = json.loads(session.qa_log)
    report_data = ai.generate_report(qa_log, session.job_role)

    report = models.InterviewReport(
        session_id=session.id,
        overall_score=report_data["overall_score"],
        technical_score=report_data["technical_score"],
        communication_score=report_data["communication_score"],
        problem_solving_score=report_data["problem_solving_score"],
        confidence_score=report_data["confidence_score"],
        strengths=report_data["strengths"],
        improvements=report_data["improvements"],
        recommended_topics=report_data["recommended_topics"],
    )
    db.add(report)
    session.status = "completed"
    db.commit()

    return schemas.ReportResponse(**report_data)


@router.get("/report/{session_id}", response_model=schemas.ReportResponse)
def get_report(
    session_id: int,
    token_payload: dict = Depends(auth.decode_token),
    db: Session = Depends(get_db),
):
    report = db.query(models.InterviewReport).filter(
        models.InterviewReport.session_id == session_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return schemas.ReportResponse(
        overall_score=report.overall_score,
        technical_score=report.technical_score,
        communication_score=report.communication_score,
        problem_solving_score=report.problem_solving_score,
        confidence_score=report.confidence_score,
        strengths=report.strengths,
        improvements=report.improvements,
        recommended_topics=report.recommended_topics,
    )
