from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.skill import SkillOut
from app.services.profile_service import get_all_skills

router = APIRouter(prefix="/skills", tags=["Danh mục kỹ năng (Skills)"])


@router.get("", response_model=list[SkillOut], summary="Lấy danh mục kỹ năng chuẩn (HS-02)")
def list_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh mục toàn bộ kỹ năng chuẩn:
    - Sắp xếp theo nhóm (skill_group) rồi theo tên (name)
    - Tất cả người dùng đã đăng nhập (ứng viên hoặc NTD) đều gọi được
    """
    return get_all_skills(db)
