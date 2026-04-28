"""User configuration router"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import UserConfig, User
from auth import verify_token
from pydantic import BaseModel

router = APIRouter(prefix="/config", tags=["config"])

class ConfigUpdate(BaseModel):
    keywords: str
    experience_summary: str
    email_frequency: str

@router.get("/")
def get_config(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get user configuration"""
    user = db.query(User).filter(User.email == email).first()
    config = db.query(UserConfig).filter(UserConfig.user_id == user.id).first()
    return config

@router.put("/")
def update_config(
    config_update: ConfigUpdate,
    email: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Update user configuration"""
    user = db.query(User).filter(User.email == email).first()
    config = db.query(UserConfig).filter(UserConfig.user_id == user.id).first()
    
    if not config:
        config = UserConfig(user_id=user.id)
    
    config.keywords = config_update.keywords
    config.experience_summary = config_update.experience_summary
    config.email_frequency = config_update.email_frequency
    
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return config
