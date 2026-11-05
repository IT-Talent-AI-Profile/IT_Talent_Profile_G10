from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (CheckConstraint("min_years >= 0", name="chk_jobs_min_years"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    recruiter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text)
    min_years = Column(Float, default=0)
    is_open = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    recruiter = relationship("User", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan", passive_deletes=True)
