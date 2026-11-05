from sqlalchemy import Column, Integer, String
from app.db.base import Base


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    skill_group = Column(String(50), nullable=False)
