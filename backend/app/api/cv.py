from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_candidate
from app.db.session import get_db
from app.models.user import User
from app.schemas.cv import CvConfirmIn, CvStatusOut
from app.schemas.profile import ProfileOut
from app.services.cv_service import confirm_cv, get_cv_status, process_cv_upload
from app.utils.pdf_parser import MAX_PDF_SIZE


router = APIRouter(prefix="/cv", tags=["CV"])


@router.post("/upload", response_model=CvStatusOut, summary="Tải CV PDF và phân tích bằng AI")
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_candidate),
    db: Session = Depends(get_db),
):
    # Đọc tối đa 5 MB + 1 byte để phát hiện file quá dung lượng mà không nạp file lớn vào RAM.
    file_content = await file.read(MAX_PDF_SIZE + 1)
    return process_cv_upload(db, current_user, file.filename, file_content)


@router.get("/{cv_id}", response_model=CvStatusOut, summary="Xem kết quả phân tích CV")
def read_cv(
    cv_id: int,
    current_user: User = Depends(get_candidate),
    db: Session = Depends(get_db),
):
    return get_cv_status(db, current_user, cv_id)


@router.post("/{cv_id}/confirm", response_model=ProfileOut, summary="Xác nhận và lưu dữ liệu CV vào hồ sơ")
def confirm_cv_result(
    cv_id: int,
    request: CvConfirmIn,
    current_user: User = Depends(get_candidate),
    db: Session = Depends(get_db),
):
    return confirm_cv(db, current_user, cv_id, request)
