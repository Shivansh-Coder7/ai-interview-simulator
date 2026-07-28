# AI Interview Simulator

Positiveway Solutions — Intern Project 3

Stack: React + Tailwind CSS · FastAPI · MySQL · Gemini API

## Setup

### 1. MySQL

Create the database (in MySQL Workbench, CLI, or a hosted MySQL instance):

```sql
CREATE DATABASE interview_simulator;
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

copy .env.example .env       # Windows
# cp .env.example .env       # Mac/Linux
```

Edit `.env` with your real MySQL password and your Gemini API key
(get one free at https://aistudio.google.com/apikey).

Create your admin login:

```bash
python create_admin.py
```

Run the server:

```bash
uvicorn app.main:app --reload
```

Backend now running at `http://localhost:8000` — test all endpoints at `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend now running at `http://localhost:5173`.

## How it works

1. Candidate signs up / logs in.
2. Uploads a resume (PDF) — text is extracted and stored.
3. Picks job role, interview type, and difficulty, then starts an interview.
4. Chats with the AI interviewer one question at a time — each question is
   generated fresh by Gemini based on the resume, role, difficulty, and
   everything answered so far.
5. After a fixed number of questions, a full performance report is generated
   (overall score, category scores, strengths, improvements, recommended
   topics) and shown to the candidate.
6. Admin logs in separately and sees platform-wide stats: total users, total
   interviews, average score, most-selected roles, and recent activity.

## Project structure

```
backend/
  app/
    main.py          FastAPI app + router wiring
    database.py       DB connection/session
    models.py          SQLAlchemy tables
    schemas.py          Request/response shapes
    auth.py               JWT + password hashing
    resume.py              PDF text extraction
    ai.py                    All Gemini calls
    routers/
      candidate.py
      interview.py
      admin.py
  create_admin.py     One-time script to create an admin login

frontend/
  src/
    pages/
      Login.jsx
      CandidateDashboard.jsx
      InterviewChat.jsx
      Report.jsx
      AdminDashboard.jsx
    api.js            Central axios client (attaches JWT automatically)
    App.jsx           Routes
```

## Notes

- Interview length is fixed at 7 questions (see `MAX_QUESTIONS` in
  `app/routers/interview.py`) — change that number if you want a shorter or
  longer interview.
- There's no admin signup route on purpose — run `create_admin.py` once to
  create your own admin login.
- CORS is currently locked to `http://localhost:5173`. If you deploy the
  frontend elsewhere, update `allow_origins` in `app/main.py`.
