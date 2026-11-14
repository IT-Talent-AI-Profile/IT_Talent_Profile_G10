import os
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.profile import Profile
from app.models.profile_skill import ProfileSkill
from app.models.cv_file import CvFile
from app.models.skill import Skill
from app.schemas.profile import ProfileUpdate, ProfileSkillIn, ProfileSkillOut, ProfileOut
from app.schemas.skill import SkillOut


def format_profile_out(profile: Profile) -> ProfileOut:
    """Format đối tượng Profile SQLAlchemy thành ProfileOut schema."""
    skills_out = []
    for ps in profile.skills:
        skills_out.append(
            ProfileSkillOut(
                skill_id=ps.skill_id,
                name=ps.skill.name if ps.skill else "",
                group=ps.skill.skill_group if ps.skill else "",
                proficiency=ps.proficiency,
                years_used=float(ps.years_used) if ps.years_used is not None else 0.0,
            )
        )

    return ProfileOut(
        id=profile.id,
        full_name=profile.full_name,
        desired_position=profile.desired_position,
        years_experience=float(profile.years_experience) if profile.years_experience is not None else 0.0,
        education=profile.education,
        experience=profile.experience,
        github_url=profile.github_url,
        is_public=bool(profile.is_public),
        level=profile.level,
        total_score=profile.total_score,
        ai_summary=profile.ai_summary,
        skills=skills_out,
    )


def get_my_profile(db: Session, user_id: int) -> ProfileOut:
    """Lấy thông tin hồ sơ của ứng viên hiện tại kèm danh sách kỹ năng (HS-01)."""
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ của người dùng"
        )
    return format_profile_out(profile)


def update_my_profile(db: Session, user_id: int, req: ProfileUpdate) -> ProfileOut:
    """Cập nhật thông tin hồ sơ của ứng viên (HS-01)."""
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ của người dùng"
        )

    profile.full_name = req.full_name
    profile.desired_position = req.desired_position
    profile.years_experience = req.years_experience
    profile.education = req.education
    profile.experience = req.experience
    profile.github_url = req.github_url
    profile.is_public = req.is_public

    db.commit()
    db.refresh(profile)
    return format_profile_out(profile)


def add_or_update_profile_skill(db: Session, user_id: int, req: ProfileSkillIn) -> ProfileOut:
    """
    Thêm hoặc cập nhật kỹ năng trong hồ sơ ứng viên (Upsert) (HS-02):
    - skill_id không tồn tại trong DB -> 404
    - Đã có skill_id -> cập nhật proficiency và years_used
    - Chưa có -> thêm dòng mới
    - Trả về hồ sơ mới nhất (ProfileOut)
    """
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ của người dùng"
        )

    # Kiểm tra kỹ năng có trong danh mục không
    skill = db.query(Skill).filter(Skill.id == req.skill_id).first()
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kỹ năng không tồn tại trong danh mục"
        )

    profile_skill = db.query(ProfileSkill).filter(
        ProfileSkill.profile_id == profile.id,
        ProfileSkill.skill_id == req.skill_id
    ).first()

    if profile_skill:
        profile_skill.proficiency = req.proficiency
        profile_skill.years_used = req.years_used
    else:
        profile_skill = ProfileSkill(
            profile_id=profile.id,
            skill_id=req.skill_id,
            proficiency=req.proficiency,
            years_used=req.years_used
        )
        db.add(profile_skill)

    db.commit()
    db.refresh(profile)
    return format_profile_out(profile)


def remove_profile_skill(db: Session, user_id: int, skill_id: int) -> ProfileOut:
    """
    Xóa kỹ năng khỏi hồ sơ ứng viên (HS-02):
    - Chưa có kỹ năng đó -> 404
    - Trả về hồ sơ mới nhất (ProfileOut)
    """
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ của người dùng"
        )

    profile_skill = db.query(ProfileSkill).filter(
        ProfileSkill.profile_id == profile.id,
        ProfileSkill.skill_id == skill_id
    ).first()

    if not profile_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hồ sơ chưa có kỹ năng này"
        )

    db.delete(profile_skill)
    db.commit()
    db.refresh(profile)
    return format_profile_out(profile)


def get_all_skills(db: Session) -> list[SkillOut]:
    """Lấy danh mục kỹ năng chuẩn sắp theo nhóm rồi theo tên (HS-02)."""
    skills = db.query(Skill).order_by(Skill.skill_group.asc(), Skill.name.asc()).all()
    return [
        SkillOut(id=s.id, name=s.name, group=s.skill_group)
        for s in skills
    ]


def delete_my_profile_and_account(db: Session, user_id: int) -> dict:
    """
    Xóa hồ sơ và toàn bộ tài khoản của ứng viên (HS-04):
    1. Kiểm tra tài khoản người dùng và hồ sơ.
    2. Xóa các file CV vật lý lưu trong thư mục uploads/ (nếu có) để tránh file mồ côi.
    3. Xóa User khỏi database -> Kích hoạt xóa dây chuyền (CASCADE) xóa profiles,
       profile_skills, cv_files trong DB.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản người dùng"
        )

    # Xóa các file CV vật lý liên quan trong thư mục uploads nếu có
    if user.profile:
        cv_files = db.query(CvFile).filter(CvFile.profile_id == user.profile.id).all()
        for cf in cv_files:
            if cf.file_path and os.path.exists(cf.file_path):
                try:
                    os.remove(cf.file_path)
                except OSError:
                    pass

    # Xóa user (database và SQLAlchemy relationship sẽ tự động cascade xóa profiles, profile_skills, cv_files)
    db.delete(user)
    db.commit()

    return {"message": "Đã xóa hồ sơ và tài khoản thành công"}

