import logging
from database import SessionLocal
from models import SentJob

logger = logging.getLogger(__name__)

def is_already_sent(job_id: str) -> bool:
    db = SessionLocal()
    try:
        exists = db.query(SentJob).filter(SentJob.job_id == job_id).first()
        return exists is not None
    finally:
        db.close()

def mark_as_sent(job_id: str, job_title: str, company: str):
    db = SessionLocal()
    try:
        entry = SentJob(job_id=job_id, title=job_title, company=company)
        db.add(entry)
        db.commit()
        logger.info(f"Marked as sent: {job_title} @ {company}")
    finally:
        db.close()

def filter_new_jobs(jobs: list) -> list:
    new_jobs = [j for j in jobs if not is_already_sent(j["job_id"])]
    logger.info(f"{len(new_jobs)} new jobs (out of {len(jobs)} total)")
    return new_jobs