from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cv_file import CvFile
from app.models.profile import Profile
from app.models.profile_skill import ProfileSkill
from app.models.skill import Skill
from app.models.user import User
from app.schemas.cv import CvAnalysisOut, CvConfirmIn, CvSkillOut, CvStatusOut
from app.schemas.profile import ProfileOut
from app.services.ai_client import extract_cv
from app.services.profile_service import format_profile_out
from app.utils.pdf_parser import (
    InvalidPdfError,
    MAX_PDF_SIZE,
    PdfEncryptedError,
    PdfNoTextError,
    PdfTooLargeError,
    extract_pdf_text,
)


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"


def _get_candidate_profile(db: Session, user: User) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ ứng viên",
        )
    return profile


def _safe_original_name(file_name: str | None) -> str:
    normalized = (file_name or "").replace("\\", "/")
    return Path(normalized).name[:255]


def _save_cv_record(
    db: Session,
    profile: Profile,
    original_name: str,
    content: bytes,
    *,
    state: str,
    error_message: str | None = None,
    ai_result: dict | None = None,
) -> CvFile:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}.pdf"
    stored_path = UPLOAD_DIR / stored_name
    stored_path.write_bytes(content)

    cv_file = CvFile(
        profile_id=profile.id,
        file_name=original_name,
        file_path=f"uploads/{stored_name}",
        file_size=len(content),
        status=state,
        error_message=error_message,
        ai_result=ai_result,
    )
    try:
        db.add(cv_file)
        db.commit()
        db.refresh(cv_file)
    except Exception:
        db.rollback()
        stored_path.unlink(missing_ok=True)
        raise

    return cv_file


def _status_output(cv_file: CvFile) -> CvStatusOut:
    result = None
    if cv_file.ai_result:
        try:
            result = CvAnalysisOut.model_validate(cv_file.ai_result)
        except (TypeError, ValueError):
            result = None

    return CvStatusOut(
        cv_id=cv_file.id,
        status=cv_file.status,
        error_message=cv_file.error_message,
        result=result,
    )


def process_cv_upload(
    db: Session,
    user: User,
    file_name: str | None,
    file_content: bytes,
) -> CvStatusOut:
    """Store a candidate PDF privately, extract text, analyze it, and persist the draft result."""
    original_name = _safe_original_name(file_name)
    if not original_name or Path(original_name).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ chấp nhận file CV có định dạng PDF",
        )

    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File PDF không được để trống",
        )
    if len(file_content) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Dung lượng CV không được vượt quá 5 MB",
        )

    profile = _get_candidate_profile(db, user)

    try:
        cv_text = extract_pdf_text(file_content)
    except PdfNoTextError as error:
        failed_file = _save_cv_record(
            db, profile, original_name, file_content,
            state="failed", error_message=str(error),
        )
        return _status_output(failed_file)
    except PdfTooLargeError as error:
        raise HTTPException(status_code=413, detail=str(error)) from error
    except (InvalidPdfError, PdfEncryptedError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    cv_file = _save_cv_record(
        db, profile, original_name, file_content, state="pending"
    )

    try:
        skills = db.query(Skill).order_by(Skill.name.asc()).all()
        skill_by_name = {item.name.casefold(): item for item in skills}
        ai_result = extract_cv(cv_text, [item.name for item in skills])

        mapped_skills = []
        skills_not_found = []
        for ai_skill in ai_result.skills:
            matched = skill_by_name.get(ai_skill.name.casefold())
            if matched is None:
                skills_not_found.append(ai_skill.name)
                continue
            mapped_skills.append(
                CvSkillOut(
                    skill_id=matched.id,
                    name=matched.name,
                    proficiency=ai_skill.proficiency,
                    years_used=ai_skill.years,
                )
            )

        analysis = CvAnalysisOut(
            cv_id=cv_file.id,
            skills=mapped_skills,
            skills_not_found=skills_not_found,
            years_experience=ai_result.years_experience,
            education=ai_result.education,
            experience=ai_result.experience,
        )
        cv_file.ai_result = analysis.model_dump()
        cv_file.status = "success"
        cv_file.error_message = None
        db.commit()
        db.refresh(cv_file)
    except Exception as error:
        db.rollback()
        failed_file = db.query(CvFile).filter(CvFile.id == cv_file.id).first()
        if failed_file is None:
            raise
        failed_file.status = "failed"
        failed_file.error_message = str(error)[:2000]
        db.commit()
        db.refresh(failed_file)
        return _status_output(failed_file)

    return _status_output(cv_file)


def get_cv_status(db: Session, user: User, cv_id: int) -> CvStatusOut:
    profile = _get_candidate_profile(db, user)
    cv_file = (
        db.query(CvFile)
        .filter(CvFile.id == cv_id, CvFile.profile_id == profile.id)
        .first()
    )
    if cv_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy CV hoặc bạn không có quyền truy cập",
        )
    return _status_output(cv_file)


def confirm_cv(
    db: Session,
    user: User,
    cv_id: int,
    request: CvConfirmIn,
) -> ProfileOut:
    """Persist the candidate-edited CV fields and skills into their own profile."""
    profile = _get_candidate_profile(db, user)
    cv_file = (
        db.query(CvFile)
        .filter(CvFile.id == cv_id, CvFile.profile_id == profile.id)
        .first()
    )
    if cv_file is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy CV")
    if cv_file.status not in {"success", "confirmed"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CV chưa phân tích thành công nên không thể xác nhận",
        )

    skill_ids = [item.skill_id for item in request.skills]
    if len(skill_ids) != len(set(skill_ids)):
        raise HTTPException(status_code=422, detail="Danh sách kỹ năng bị trùng")

    skill_rows = (
        db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
        if skill_ids else []
    )
    skill_by_id = {item.id: item for item in skill_rows}
    missing_ids = sorted(set(skill_ids) - set(skill_by_id))
    if missing_ids:
        raise HTTPException(
            status_code=422,
            detail=f"Kỹ năng không tồn tại trong danh mục: {missing_ids}",
        )

    try:
        db.query(ProfileSkill).filter(ProfileSkill.profile_id == profile.id).delete(
            synchronize_session=False
        )
        for item in request.skills:
            db.add(
                ProfileSkill(
                    profile_id=profile.id,
                    skill_id=item.skill_id,
                    proficiency=item.proficiency,
                    years_used=item.years_used,
                )
            )

        profile.years_experience = request.years_experience
        profile.education = request.education
        profile.experience = request.experience

        confirmed_result = CvAnalysisOut(
            cv_id=cv_file.id,
            skills=[
                CvSkillOut(
                    skill_id=item.skill_id,
                    name=skill_by_id[item.skill_id].name,
                    proficiency=item.proficiency,
                    years_used=item.years_used,
                )
                for item in request.skills
            ],
            skills_not_found=[],
            years_experience=request.years_experience,
            education=request.education,
            experience=request.experience,
        )
        cv_file.ai_result = confirmed_result.model_dump()
        cv_file.status = "confirmed"
        cv_file.error_message = None
        db.commit()
        db.refresh(profile)
    except Exception:
        db.rollback()
        raise

    return format_profile_out(profile)
