from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from app.db.base import Base


class ProfileSkill(Base):
    __tablename__ = "profile_skills"
    __table_args__ = (
        UniqueConstraint("profile_id", "skill_id", name="uq_profile_skill"),
        CheckConstraint("proficiency BETWEEN 1 AND 5", name="chk_profile_skills_proficiency"),
        CheckConstraint("years_used >= 0", name="chk_profile_skills_years"),
        Index("idx_profile_skills_skill", "skill_id"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False)
    proficiency = Column(TINYINT, nullable=False)
    years_used = Column(Float, default=0)
    profile = relationship("Profile", back_populates="skills")
    skill = relationship("Skill")
