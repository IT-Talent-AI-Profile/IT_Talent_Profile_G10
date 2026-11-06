from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class CvFile(Base):
    __tablename__ = "cv_files"
    __table_args__ = (
        CheckConstraint("file_size <= 5242880", name="chk_cv_files_size"),
        CheckConstraint("status IN ('pending', 'success', 'failed', 'confirmed')", name="chk_cv_files_status"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    status = Column(String(20), nullable=False)
    ai_result = Column(JSON)
    error_message = Column(Text)
    uploaded_at = Column(DateTime, server_default=func.now())
    profile = relationship("Profile", back_populates="cv_files")
