from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'candidate' hoặc 'recruiter'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Quan hệ 1-1 với Profile
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
