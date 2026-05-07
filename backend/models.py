from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class SentJob(Base):
    __tablename__ = "sent_jobs"
    job_id  = Column(String, primary_key=True, index=True)
    title   = Column(String, nullable=False)
    company = Column(String, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    email      = Column(String, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserConfig(Base):
    __tablename__ = "user_config"
    email             = Column(String, primary_key=True, index=True)
    role              = Column(String, default="Product Manager")
    years_exp         = Column(String, default="5")
    domain            = Column(String, default="")
    location          = Column(String, default="India")
    time_filter       = Column(String, default="24h")
    notify_email      = Column(String, default="")
    schedule_interval = Column(String, default="1h")
    updated_at        = Column(DateTime(timezone=True), onupdate=func.now())