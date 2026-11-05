from typing import Optional
from pydantic import BaseModel


class EvaluationOut(BaseModel):
    total_score: float
    level: str
    groups: dict[str, float]
    summary: Optional[str] = None
