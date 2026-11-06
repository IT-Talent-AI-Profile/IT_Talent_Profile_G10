from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from app.services.auth_service import register_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["Xác thực (Auth)"])

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_200_OK, summary="Đăng ký tài khoản")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Đăng ký tài khoản ứng viên hoặc nhà tuyển dụng:
    - role: 'candidate' hoặc 'recruiter'
    - password: tối thiểu 8 ký tự
    - Tự động tạo bản ghi profiles nếu là candidate
    """
    return register_user(db, req)

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK, summary="Đăng nhập hệ thống")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Đăng nhập lấy JWT token:
    - Trả về token và role người dùng
    - Sai email hoặc mật khẩu trả về 401: 'Email hoặc mật khẩu không đúng'
    """
    return authenticate_user(db, req)
