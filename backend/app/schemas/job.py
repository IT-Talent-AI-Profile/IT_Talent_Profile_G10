from typing import Optional
from pydantic import BaseModel, Field


class JobIn(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    min_years: float = Field(default=0, ge=0)


class JobStatusIn(BaseModel):
    is_open: bool


class JobSkillIn(BaseModel):
    skill_id: int
    is_required: bool


class JobSkillOut(BaseModel):
    skill_id: int
    name: str
    is_required: bool


class JobOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    min_years: float = 0
    is_open: bool = True
    skills: list[JobSkillOut] = []
