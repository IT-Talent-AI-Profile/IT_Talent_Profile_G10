from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_candidate
from app.db.session import get_db
from app.models.user import User
from app.schemas.evaluation import EvaluationOut
from app.services.cv_service import _get_candidate_profile
from app.services.evaluation_service import recalculate_profile_evaluation


router = APIRouter(prefix="/evaluation", tags=["Đánh giá (Evaluation)"])


@router.get("/me", response_model=EvaluationOut, summary="Xem kết quả đánh giá năng lực")
def read_my_evaluation(
    current_user: User = Depends(get_candidate),
    db: Session = Depends(get_db),
):
    profile = _get_candidate_profile(db, current_user)
    return recalculate_profile_evaluation(db, profile)
