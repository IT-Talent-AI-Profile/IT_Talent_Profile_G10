from typing import Optional
from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    desired_position: Optional[str] = Field(default=None, max_length=100)
    years_experience: float = Field(default=0, ge=0)
    education: Optional[str] = None
    experience: Optional[str] = None
    github_url: Optional[str] = Field(default=None, max_length=255)
    is_public: bool = False


class ProfileSkillIn(BaseModel):
    skill_id: int
    proficiency: int = Field(ge=1, le=5)
    years_used: float = Field(default=0, ge=0)


class ProfileSkillOut(BaseModel):
    skill_id: int
    name: str
    group: str
    proficiency: int
    years_used: float


class ProfileOut(BaseModel):
    id: int
    full_name: str
    desired_position: Optional[str] = None
    years_experience: float = 0
    education: Optional[str] = None
    experience: Optional[str] = None
    github_url: Optional[str] = None
    is_public: bool = False
    level: Optional[str] = None
    total_score: Optional[float] = None
    ai_summary: Optional[str] = None
    skills: list[ProfileSkillOut] = []
