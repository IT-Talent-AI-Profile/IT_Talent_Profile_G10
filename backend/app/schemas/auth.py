from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = Field(default=None, max_length=100)
    role: Literal["candidate", "recruiter"]

class RegisterResponse(BaseModel):
    message: str = "Đăng ký thành công"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    token: str
    role: str

# Aliases tương thích ngược
RegisterRequest = RegisterIn
LoginRequest = LoginIn
LoginResponse = TokenOut
