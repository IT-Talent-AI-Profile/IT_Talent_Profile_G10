from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base

class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (Index("idx_profiles_public_level", "is_public", "level"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    desired_position = Column(String(100))
    years_experience = Column(Float, default=0)
    education = Column(Text)
    experience = Column(Text)
    github_url = Column(String(255))
    is_public = Column(Boolean, default=False)
    level = Column(String(20))
    total_score = Column(Float)
    ai_summary = Column(Text)
    user = relationship("User", back_populates="profile")
    skills = relationship("ProfileSkill", back_populates="profile", cascade="all, delete-orphan", passive_deletes=True)
    cv_files = relationship("CvFile", back_populates="profile", cascade="all, delete-orphan", passive_deletes=True)
