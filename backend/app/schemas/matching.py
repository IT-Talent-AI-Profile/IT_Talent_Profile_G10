from typing import Optional
from pydantic import BaseModel


class CandidateItem(BaseModel):
    id: int
    full_name: str
    desired_position: Optional[str] = None
    years_experience: float = 0
    level: Optional[str] = None
    total_score: Optional[float] = None


class CandidateList(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[CandidateItem]


class MatchItem(CandidateItem):
    match_percent: float
    matched_skills: list[str]
    missing_skills: list[str]


class MatchList(BaseModel):
    job: str
    total: int
    page: int
    page_size: int
    items: list[MatchItem]
