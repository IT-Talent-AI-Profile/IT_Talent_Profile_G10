from sqlalchemy import Column, Integer, String, Float, Text, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    desired_position = Column(String(100), nullable=True)
    years_experience = Column(Float, default=0.0)
    education = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    github_url = Column(String(255), nullable=True)
    is_public = Column(SmallInteger, default=0)
    level = Column(String(20), nullable=True)
    total_score = Column(Float, nullable=True)
    ai_summary = Column(Text, nullable=True)

    # Quan hệ ngược về User
    user = relationship("User", back_populates="profile")
