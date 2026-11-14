from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import get_candidate
from app.schemas.profile import ProfileUpdate, ProfileSkillIn, ProfileOut
from app.services.profile_service import (
    get_my_profile,
    update_my_profile,
    add_or_update_profile_skill,
    remove_profile_skill,
    delete_my_profile_and_account,
)

router = APIRouter(prefix="/profiles", tags=["Hồ sơ ứng viên (Profiles)"])


@router.get("/me", response_model=ProfileOut, summary="Xem hồ sơ cá nhân (HS-01)")
def read_my_profile(
    current_user: User = Depends(get_candidate),
    db: Session = Depends(get_db)
):
    """
    Xem hồ sơ cá nhân của ứng viên hiện tại:
    - Chỉ ứng viên có quyền truy cập (NTD gọi -> 403)
    - Trả về thông tin chi tiết kèm danh sách kỹ năng
    """
    return get_my_profile(db, current_user.id)


@router.put("/me", response_model=ProfileOut, summary="Cập nhật hồ sơ cá nhân (HS-01)")
def edit_my_profile(
    req: ProfileUpdate,
    current_user: User = Depends(get_candidate),
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin hồ sơ:
    - full_name, desired_position, years_experience (>= 0), education, experience, github_url, is_public
    - Chỉ ứng viên có quyền truy cập
    """
    return update_my_profile(db, current_user.id, req)


@router.post("/me/skills", response_model=ProfileOut, summary="Thêm hoặc cập nhật kỹ năng vào hồ sơ (HS-02)")
def add_skill_to_profile(
    req: ProfileSkillIn,
    current_user: User = Depends(get_candidate),
    db: Session = Depends(get_db)
):
    """
    Thêm hoặc cập nhật kỹ năng trong hồ sơ (Upsert):
    - proficiency: từ 1 đến 5
    - years_used: >= 0
    - Kỹ năng không tồn tại trong danh mục -> 404
    - Trả lại hồ sơ mới nhất
    """
    return add_or_update_profile_skill(db, current_user.id, req)


@router.delete("/me/skills/{skill_id}", response_model=ProfileOut, summary="Xóa kỹ năng khỏi hồ sơ (HS-02)")
def delete_skill_from_profile(
    skill_id: int,
    current_user: User = Depends(get_candidate),
    db: Session = Depends(get_db)
):
    """
    Xóa một kỹ năng khỏi hồ sơ của ứng viên:
    - Hồ sơ chưa có kỹ năng -> 404
    - Trả lại hồ sơ mới nhất
    """
    return remove_profile_skill(db, current_user.id, skill_id)


@router.delete("/me", summary="Xóa hồ sơ và tài khoản ứng viên (HS-04)")
def delete_my_account_and_profile(
    current_user: User = Depends(get_candidate),
    db: Session = Depends(get_db)
):
    """
    Xóa vĩnh viễn hồ sơ và tài khoản của ứng viên:
    - Xóa các file CV vật lý trong thư mục uploads/ nếu có (tránh file mồ côi)
    - Xóa tài khoản người dùng và tự động cascade xóa toàn bộ dữ liệu liên quan
    """
    return delete_my_profile_and_account(db, current_user.id)

