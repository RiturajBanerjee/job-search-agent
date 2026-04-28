from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from database import Base

class SentJob(Base):
    __tablename__ = "sent_jobs"

    job_id    = Column(String, primary_key=True, index=True)
    title     = Column(String, nullable=False)
    company   = Column(String, nullable=False)
    sent_at   = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SentJob job_id={self.job_id} title={self.title}>"