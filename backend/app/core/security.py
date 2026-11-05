import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

def hash_password(password: str) -> str:
    """Băm mật khẩu bằng bcrypt với salt tự động tạo ngẫu nhiên."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu nhập vào có khớp với chuỗi băm bcrypt không."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_token(data: dict, expires_minutes: int = None) -> str:
    """
    Tạo JSON Web Token (JWT) có thời hạn (mặc định 60 phút).
    data có thể chứa id người dùng, role, email...
    """
    to_encode = data.copy()
    expire_minutes = expires_minutes if expires_minutes is not None else settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# Alias tương thích
create_access_token = create_token

def decode_token(token: str) -> dict:
    """
    Giải mã và kiểm tra tính hợp lệ của token JWT.
    Báo lỗi khi token hết hạn (ExpiredSignatureError) hoặc sai SECRET_KEY/không hợp lệ (InvalidTokenError).
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token đã hết hạn")
    except jwt.InvalidTokenError:
        raise ValueError("Token không hợp lệ hoặc sai chữ ký")
