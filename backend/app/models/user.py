from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('candidate', 'recruiter')", name="chk_users_role"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan", passive_deletes=True)
