from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Mật khẩu tối thiểu 8 ký tự")
    full_name: Optional[str] = Field(None, description="Họ và tên của ứng viên")
    role: Literal["candidate", "recruiter"] = Field(..., description="Vai trò: candidate hoặc recruiter")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu phải có từ 8 ký tự trở lên")
        return v

class RegisterResponse(BaseModel):
    message: str = "Đăng ký thành công"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class LoginResponse(BaseModel):
    token: str
    role: str
