from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_candidate,
    get_current_user,
    get_recruiter,
)
from app.models.user import User

router = APIRouter(tags=["Kiểm tra phân quyền"])


def user_info(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
    }


@router.get("/auth/me", summary="Thông tin người dùng đang đăng nhập")
def read_current_user(current_user: User = Depends(get_current_user)):
    return user_info(current_user)


@router.get("/candidate/me", summary="Kiểm tra quyền ứng viên")
def read_candidate(current_user: User = Depends(get_candidate)):
    return user_info(current_user)


@router.get("/recruiter/me", summary="Kiểm tra quyền nhà tuyển dụng")
def read_recruiter(current_user: User = Depends(get_recruiter)):
    return user_info(current_user)
