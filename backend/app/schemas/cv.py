from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.profile import ProfileSkillIn


class AiSkill(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    proficiency: int = Field(ge=1, le=5)
    years: float = Field(default=0, ge=0)


class CvResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skills: list[AiSkill] = Field(default_factory=list)
    years_experience: float = Field(default=0, ge=0)
    education: Optional[str] = None
    experience: Optional[str] = None


class CvSkillOut(BaseModel):
    skill_id: int
    name: str
    proficiency: int = Field(ge=1, le=5)
    years_used: float = Field(default=0, ge=0)


class CvAnalysisOut(BaseModel):
    cv_id: int
    skills: list[CvSkillOut] = Field(default_factory=list)
    skills_not_found: list[str] = Field(default_factory=list)
    years_experience: float = Field(default=0, ge=0)
    education: Optional[str] = None
    experience: Optional[str] = None


class CvStatusOut(BaseModel):
    cv_id: int
    status: str
    error_message: Optional[str] = None
    result: Optional[CvAnalysisOut] = None


class CvConfirmIn(BaseModel):
    skills: list[ProfileSkillIn] = Field(default_factory=list)
    years_experience: float = Field(default=0, ge=0)
    education: Optional[str] = None
    experience: Optional[str] = None
