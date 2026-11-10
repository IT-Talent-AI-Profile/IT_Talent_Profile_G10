from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api.dependencies import get_recruiter
from app.schemas.job import JobIn, JobOut, JobStatusIn, JobSkillIn
from app.services.job_service import (
    create_job,
    list_jobs,
    get_job,
    update_job,
    delete_job,
    set_status,
    add_skill,
    remove_skill,
)

router = APIRouter(prefix="/jobs", tags=["Việc làm (Jobs)"])


@router.post("", response_model=JobOut, summary="Tạo JD mới (JD-03)")
def create(data: JobIn, current_user: User = Depends(get_recruiter), db: Session = Depends(get_db)):
    return create_job(db, current_user.id, data)


@router.get("", response_model=list[JobOut], summary="Danh sách JD của tôi (JD-03)")
def list_my_jobs(current_user: User = Depends(get_recruiter), db: Session = Depends(get_db)):
    return list_jobs(db, current_user.id)


@router.get("/{job_id}", response_model=JobOut, summary="Xem chi tiết JD (JD-03)")
def read(job_id: int, current_user: User = Depends(get_recruiter), db: Session = Depends(get_db)):
    return get_job(db, current_user.id, job_id)


@router.put("/{job_id}", response_model=JobOut, summary="Sửa JD (JD-03)")
def update(job_id: int, data: JobIn, current_user: User = Depends(get_recruiter), db: Session = Depends(get_db)):
    return update_job(db, current_user.id, job_id, data)


@router.delete("/{job_id}", summary="Xóa JD (JD-03)")
def delete(job_id: int, current_user: User = Depends(get_recruiter), db: Session = Depends(get_db)):
    delete_job(db, current_user.id, job_id)
    return {"message": "Đã xóa JD"}


@router.patch("/{job_id}/status", response_model=JobOut, summary="Đóng hoặc mở JD (JD-03)")
def change_status(job_id: int, data: JobStatusIn, current_user: User = Depends(get_recruiter), db: Session = Depends(get_db)):
    return set_status(db, current_user.id, job_id, data.is_open)


@router.post("/{job_id}/skills", response_model=JobOut, summary="Gắn kỹ năng vào JD (JD-03)")
def attach_skill(job_id: int, data: JobSkillIn, current_user: User = Depends(get_recruiter), db: Session = Depends(get_db)):
    return add_skill(db, current_user.id, job_id, data)


@router.delete("/{job_id}/skills/{skill_id}", response_model=JobOut, summary="Gỡ kỹ năng khỏi JD (JD-03)")
def detach_skill(job_id: int, skill_id: int, current_user: User = Depends(get_recruiter), db: Session = Depends(get_db)):
    return remove_skill(db, current_user.id, job_id, skill_id)