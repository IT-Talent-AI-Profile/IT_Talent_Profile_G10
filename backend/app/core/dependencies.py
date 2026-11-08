from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.core.security import decode_token

# Sử dụng HTTPBearer để hiển thị nút Authorize trên Swagger UI /docs
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Đọc token trong header Authorization (Bearer <token>).
    Thiếu token, token hết hạn hoặc user không tồn tại -> 401.
    """
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id") or payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không chứa thông tin định danh người dùng",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def get_candidate(current_user: User = Depends(get_current_user)) -> User:
    """Chỉ cho ứng viên đi qua, sai vai trò -> 403."""
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chức năng chỉ dành cho ứng viên"
        )
    return current_user

def get_recruiter(current_user: User = Depends(get_current_user)) -> User:
    """Chỉ cho nhà tuyển dụng đi qua, sai vai trò -> 403."""
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chức năng chỉ dành cho nhà tuyển dụng"
        )
    return current_user
