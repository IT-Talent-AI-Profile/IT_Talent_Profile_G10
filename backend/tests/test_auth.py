import pytest
import jwt
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password, check_password, create_token, decode_token

client = TestClient(app)

# ==========================================
# TEST TASK [TK-01]: Hashing & JWT Security
# ==========================================
def test_password_hashing():
    pwd = "my_strong_password_123"
    h1 = hash_password(pwd)
    h2 = hash_password(pwd)
    
    # 2 lần băm phải ra 2 chuỗi khác nhau do salt ngẫu nhiên
    assert h1 != h2
    # Nhưng kiểm tra đều phải trả về True
    assert check_password(pwd, h1) is True
    assert check_password(pwd, h2) is True
    # Mật khẩu sai phải trả về False
    assert check_password("wrong_password", h1) is False

def test_jwt_token_valid():
    payload = {"user_id": 99, "role": "candidate"}
    token = create_token(payload)
    decoded = decode_token(token)
    assert decoded["user_id"] == 99
    assert decoded["role"] == "candidate"

def test_jwt_token_expired():
    payload = {"user_id": 99, "role": "candidate"}
    token = create_token(payload, expires_minutes=-1)
    with pytest.raises(ValueError, match="hết hạn"):
        decode_token(token)

def test_jwt_token_invalid_signature():
    payload = {"user_id": 99, "role": "candidate"}
    token = jwt.encode(payload, "a_completely_different_secret_key_32bytes_long!", algorithm="HS256")
    with pytest.raises(ValueError, match="không hợp lệ hoặc sai chữ ký"):
        decode_token(token)

# ==========================================
# TEST TASK [TK-02]: Register & Login API
# ==========================================
def test_login_success_sample_account():
    # Sử dụng tài khoản mẫu đã tạo ở Task NT-04
    res = client.post("/auth/login", json={
        "email": "nguyen.senior@example.com",
        "password": "12345678"
    })
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["role"] == "candidate"

def test_login_invalid_password():
    res = client.post("/auth/login", json={
        "email": "nguyen.senior@example.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401
    assert res.json()["detail"] == "Email hoặc mật khẩu không đúng"

def test_login_invalid_email():
    res = client.post("/auth/login", json={
        "email": "nonexistent_email_12345@example.com",
        "password": "12345678"
    })
    assert res.status_code == 401
    assert res.json()["detail"] == "Email hoặc mật khẩu không đúng"

def test_register_candidate_and_duplicate_error():
    rand_email = f"candidate_{uuid.uuid4().hex[:6]}@example.com"
    # 1. Đăng ký thành công
    res = client.post("/auth/register", json={
        "email": rand_email,
        "password": "valid_password_123",
        "full_name": "Nguyễn Văn Ứng Viên",
        "role": "candidate"
    })
    assert res.status_code == 200
    assert res.json()["message"] == "Đăng ký thành công"

    # 2. Đăng ký lại trùng email -> 400
    res_dup = client.post("/auth/register", json={
        "email": rand_email,
        "password": "another_password_123",
        "full_name": "Nguyễn Văn Ứng Viên Trùng",
        "role": "candidate"
    })
    assert res_dup.status_code == 400
    assert res_dup.json()["detail"] == "Email đã được đăng ký"

def test_register_validation_errors():
    # Mật khẩu dưới 8 ký tự -> 422
    res_pwd = client.post("/auth/register", json={
        "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
        "password": "123",
        "role": "candidate"
    })
    assert res_pwd.status_code == 422

    # Sai role -> 422
    res_role = client.post("/auth/register", json={
        "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
        "password": "valid_password_123",
        "role": "superadmin"
    })
    assert res_role.status_code == 422
