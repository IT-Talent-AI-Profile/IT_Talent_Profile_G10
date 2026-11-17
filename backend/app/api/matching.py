from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api.dependencies import get_recruiter
from app.schemas.matching import CandidateList
from app.schemas.profile import ProfileOut
from app.services.matching_service import search_candidates, get_candidate_detail

router = APIRouter(tags=["Đối sánh (Matching)"])


@router.get("/candidates", response_model=CandidateList, summary="Tìm kiếm ứng viên (DS-03)")
def search(skill_ids: str = "", level: str = "", page: int = Query(1, ge=1), current_user: User = Depends(get_recruiter), db: Session = Depends(get_db)):
    return search_candidates(db, skill_ids, level, page)


@router.get("/candidates/{profile_id}", response_model=ProfileOut, summary="Xem hồ sơ ứng viên công khai (DS-03)")
def read(profile_id: int, current_user: User = Depends(get_recruiter), db: Session = Depends(get_db)):
    return get_candidate_detail(db, profile_id)