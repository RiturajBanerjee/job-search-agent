"""Jobs router"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Job, User
from auth import verify_token

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/")
def get_jobs(
    email: str = Depends(verify_token),
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db)
):
    """Get jobs for current user"""
    user = db.query(User).filter(User.email == email).first()
    jobs = db.query(Job).filter(Job.user_id == user.id).offset(skip).limit(limit).all()
    return jobs

@router.post("/")
def create_job(
    job_data: dict,
    email: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a new job entry"""
    user = db.query(User).filter(User.email == email).first()
    job = Job(user_id=user.id, **job_data)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("/{job_id}")
def get_job(job_id: int, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get a specific job"""
    user = db.query(User).filter(User.email == email).first()
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    return job

@router.delete("/{job_id}")
def delete_job(job_id: int, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Delete a job"""
    user = db.query(User).filter(User.email == email).first()
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if job:
        db.delete(job)
        db.commit()
    return {"status": "deleted"}
