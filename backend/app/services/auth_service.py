from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.profile import Profile
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from app.core.security import hash_password, check_password, create_token

def register_user(db: Session, req: RegisterRequest) -> RegisterResponse:
    """
    Đăng ký tài khoản người dùng mới:
    - Kiểm tra email không được trùng (trùng trả 400 'Email đã được đăng ký').
    - Băm mật khẩu bằng bcrypt.
    - Nếu là ứng viên (role='candidate'), tự động tạo 1 bản ghi profiles.
    - NTD (role='recruiter') thì không tạo profile.
    """
    # 1. Kiểm tra email trùng
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký"
        )

    # 2. Băm mật khẩu
    hashed_pwd = hash_password(req.password)

    # 3. Tạo tài khoản User
    new_user = User(
        email=req.email,
        password_hash=hashed_pwd,
        role=req.role
    )
    db.add(new_user)
    db.flush()  # Để lấy new_user.id

    # 4. Nếu là ứng viên, tự động khởi tạo hồ sơ (Profile)
    if req.role == "candidate":
        candidate_name = req.full_name.strip() if req.full_name and req.full_name.strip() else req.email.split("@")[0]
        new_profile = Profile(
            user_id=new_user.id,
            full_name=candidate_name,
            years_experience=0.0,
            is_public=0
        )
        db.add(new_profile)

    db.commit()
    db.refresh(new_user)

    return RegisterResponse(message="Đăng ký thành công")

def authenticate_user(db: Session, req: LoginRequest) -> LoginResponse:
    """
    Đăng nhập hệ thống:
    - Kiểm tra email và mật khẩu.
    - Sai email hoặc sai mật khẩu đều trả lỗi 401: 'Email hoặc mật khẩu không đúng'.
    - Đúng thông tin trả về {token, role}.
    """
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng"
        )

    if not check_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng"
        )

    # Tạo JWT token chứa id người dùng và role
    token_data = {
        "sub": str(user.id),
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    }
    token = create_token(token_data)

    return LoginResponse(token=token, role=user.role)
