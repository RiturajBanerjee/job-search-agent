# backend/routers/config_router.py
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from auth import get_current_user
from database import SessionLocal
from models import UserConfig, User
from modules.scheduler import set_schedule, start_scheduler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/config", tags=["config"])

class ConfigRequest(BaseModel):
    role: str
    years_exp: int
    domain: Optional[str] = ""
    location: Optional[str] = "India"
    time_filter: str = "24h"
    notify_email: EmailStr
    schedule_interval: str = "1h"

def get_or_create_config(email: str):
    db = SessionLocal()
    try:
        cfg = db.query(UserConfig).filter(UserConfig.email == email).first()
        if not cfg:
            cfg = UserConfig(email=email)
            db.add(cfg)
            db.commit()
            db.refresh(cfg)
        return {
            "role":              cfg.role,
            "years_exp":         cfg.years_exp,
            "domain":            cfg.domain,
            "location":          cfg.location,
            "time_filter":       cfg.time_filter,
            "notify_email":      cfg.notify_email,
            "schedule_interval": cfg.schedule_interval,
        }
    finally:
        db.close()

@router.get("")
def get_config(current_user: User = Depends(get_current_user)):
    return get_or_create_config(current_user.email)

@router.post("")
def save_config(req: ConfigRequest, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        cfg = db.query(UserConfig).filter(UserConfig.email == current_user.email).first()
        if not cfg:
            cfg = UserConfig(email=current_user.email)
            db.add(cfg)

        cfg.role              = req.role
        cfg.years_exp         = str(req.years_exp)
        cfg.domain            = req.domain or ""
        cfg.location          = req.location or "India"
        cfg.time_filter       = req.time_filter
        cfg.notify_email      = req.notify_email
        cfg.schedule_interval = req.schedule_interval

        db.commit()
        logger.info(f"Config saved for {current_user.email}")

        # Update the scheduler with new config
        user_config_dict = {
            "role":         req.role,
            "years_exp":    req.years_exp,
            "domain":       req.domain,
            "location":     req.location,
            "time_filter":  req.time_filter,
            "notify_email": req.notify_email,
        }
        set_schedule(req.schedule_interval, user_config_dict)

        return {"status": "saved"}
    finally:
        db.close()