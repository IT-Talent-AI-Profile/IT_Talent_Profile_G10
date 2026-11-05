from pydantic import BaseModel


class SkillOut(BaseModel):
    id: int
    name: str
    group: str
