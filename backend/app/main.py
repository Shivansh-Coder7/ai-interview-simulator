from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import candidate, interview, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Interview Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidate.router, prefix="/candidate", tags=["candidate"])
app.include_router(interview.router, prefix="/interview", tags=["interview"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/")
def root():
    return {"status": "AI Interview Simulator backend running"}
