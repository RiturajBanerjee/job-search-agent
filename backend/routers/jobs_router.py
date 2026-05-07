# backend/routers/jobs_router.py
import logging
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import get_current_user
from database import SessionLocal
from models import User, SentJob
from modules.search import fetch_jobs, fetch_job_description
from modules.jd_analyzer import analyze_match
from modules.dedup import filter_new_jobs, mark_as_sent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])

class SearchRequest(BaseModel):
    role: str
    years_exp: int
    domain: Optional[str] = ""
    location: Optional[str] = "India"
    time_filter: str = "24h"
    limit: int = 10

@router.post("/search")
def search_jobs(req: SearchRequest, current_user: User = Depends(get_current_user)):
    """
    Manual search triggered from the dashboard.
    Fetches jobs, runs LLM analysis, returns results.
    Does NOT send email or mark as sent — that's only for scheduled runs.
    """
    try:
        logger.info(f"Manual search by {current_user.email}: {req.role}, {req.years_exp}yrs")

        # Step 1 — fetch job cards from LinkedIn
        jobs = fetch_jobs(
            role=req.role,
            location=req.location or "India",
            time_filter=req.time_filter,
            years_exp=req.years_exp,
            limit=req.limit,
        )

        if not jobs:
            return {"jobs": [], "total": 0, "message": "No jobs found"}

        # Step 2 — fetch full JD for each job
        for job in jobs:
            fetch_job_description(job)
            time.sleep(0.5)

        # Step 3 — LLM analysis on each job
        results = []
        for job in jobs:
            try:
                match = analyze_match(
                    job,
                    years_exp=req.years_exp,
                    search_role=req.role,
                    domain=req.domain or None,
                )
                results.append({
                    "job":   match["job"],
                    "match": {
                        "score":                  match["score"],
                        "is_role_match":          match["is_role_match"],
                        "reasons":                match["reasons"],
                        "warnings":               match["warnings"],
                        "extracted_requirements": match["extracted_requirements"],
                    }
                })
                time.sleep(0.5)  # respect Gemini rate limit
            except Exception as e:
                logger.error(f"Analysis failed for {job.get('title')}: {e}")
                # Still include the job, just without analysis
                results.append({"job": job, "match": {"score": 0, "is_role_match": True,
                                                       "reasons": [], "warnings": ["Analysis failed"]}})

        # Sort by score descending
        results.sort(key=lambda x: x["match"]["score"], reverse=True)

        logger.info(f"Search complete: {len(results)} jobs returned")
        return {"jobs": results, "total": len(results)}

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
def get_recent_jobs(current_user: User = Depends(get_current_user)):
    """Returns the last 20 jobs that were emailed to the user."""
    db = SessionLocal()
    try:
        jobs = (
            db.query(SentJob)
            .order_by(SentJob.sent_at.desc())
            .limit(20)
            .all()
        )
        return [
            {
                "job_id":  j.job_id,
                "title":   j.title,
                "company": j.company,
                "sent_at": j.sent_at.isoformat() if j.sent_at else None,
            }
            for j in jobs
        ]
    finally:
        db.close()