from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.profile import ProfileSkillIn


class AiSkill(BaseModel):
    name: str
    proficiency: int = Field(ge=1, le=5)
    years: float = Field(default=0, ge=0)


class CvResult(BaseModel):
    skills: list[AiSkill]
    years_experience: float = Field(default=0, ge=0)
    education: Optional[str] = None
    experience: Optional[str] = None


class CvSkillOut(BaseModel):
    skill_id: int
    name: str
    proficiency: int
    years_used: float


class CvAnalysisOut(BaseModel):
    cv_id: int
    skills: list[CvSkillOut]
    skills_not_found: list[str] = []
    years_experience: float = 0
    education: Optional[str] = None
    experience: Optional[str] = None


class CvStatusOut(BaseModel):
    cv_id: int
    status: str
    error_message: Optional[str] = None
    result: Optional[CvAnalysisOut] = None


class CvConfirmIn(BaseModel):
    skills: list[ProfileSkillIn]
    years_experience: float = Field(default=0, ge=0)
    education: Optional[str] = None
    experience: Optional[str] = None
