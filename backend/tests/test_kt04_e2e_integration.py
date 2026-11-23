from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models import User, Profile, Skill, Job
from app.core.security import create_token
from app.services import cv_service
from app.services.ai_client import settings as ai_settings
from tests.test_pdf_parser import create_text_pdf


@pytest.fixture
def e2e_context(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSession()

    # Seed 5 kỹ năng mẫu
    py = Skill(id=1, name="Python", skill_group="Backend")
    fa = Skill(id=2, name="FastAPI", skill_group="Backend")
    sql = Skill(id=3, name="SQL", skill_group="Database")
    doc = Skill(id=4, name="Docker", skill_group="DevOps")
    rea = Skill(id=5, name="React", skill_group="Frontend")
    db.add_all([py, fa, sql, doc, rea])
    db.commit()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(cv_service, "UPLOAD_DIR", Path(tmp_path) / "private_uploads")
    monkeypatch.setattr(ai_settings, "AI_MODE", "mock")
    monkeypatch.setattr(ai_settings, "AI_API_KEY", "")

    yield TestClient(app), db

    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# KIỂM THỬ TOÀN TRÌNH HỆ THỐNG END-TO-END (KT-04)
# ============================================================

def test_e2e_complete_recruitment_lifecycle(e2e_context):
    """
    Kịch bản E2E toàn trình 7 bước của người dùng thật:
    1. Đăng ký & đăng nhập Ứng viên
    2. Tải lên CV PDF trích xuất bằng AI
    3. Xác nhận kết quả CV và lưu hồ sơ công khai
    4. Kiểm tra đánh giá năng lực tự động
    5. Đăng ký & đăng nhập Nhà tuyển dụng
    6. Nhà tuyển dụng tạo JD và gắn kỹ năng yêu cầu
    7. Đối sánh AI xếp hạng ứng viên chuẩn xác
    """
    client, db = e2e_context

    # BƯỚC 1: Đăng ký & Đăng nhập Ứng viên
    res_reg_c = client.post("/auth/register", json={
        "email": "candidate_e2e@example.com",
        "password": "Password123",
        "role": "candidate"
    })
    assert res_reg_c.status_code == 200

    res_login_c = client.post("/auth/login", json={
        "email": "candidate_e2e@example.com",
        "password": "Password123"
    })
    assert res_login_c.status_code == 200
    token_c = res_login_c.json()["token"]
    assert token_c

    # BƯỚC 2: Tải lên CV PDF
    pdf = create_text_pdf(["Senior Python Developer with FastAPI and SQL experience"])
    res_upload = client.post(
        "/cv/upload",
        headers=auth_header(token_c),
        files={"file": ("my_resume.pdf", pdf, "application/pdf")}
    )
    assert res_upload.status_code == 200
    cv_id = res_upload.json()["cv_id"]

    # BƯỚC 3: Xác nhận CV và bật hồ sơ công khai
    res_confirm = client.post(
        f"/cv/{cv_id}/confirm",
        headers=auth_header(token_c),
        json={
            "skills": [
                {"skill_id": 1, "proficiency": 4, "years_used": 3.0}, # Python
                {"skill_id": 2, "proficiency": 4, "years_used": 2.0}, # FastAPI
                {"skill_id": 3, "proficiency": 3, "years_used": 2.0}, # SQL
            ],
            "years_experience": 3.5,
            "education": "Đại học Bách Khoa",
            "experience": "3.5 năm lập trình Backend Python"
        }
    )
    assert res_confirm.status_code == 200

    # Cập nhật thông tin & bật công khai (is_public=True)
    res_update_prf = client.put(
        "/profiles/me",
        headers=auth_header(token_c),
        json={
            "full_name": "Nguyễn Văn E2E",
            "desired_position": "Senior Backend Developer",
            "years_experience": 3.5,
            "education": "Đại học Bách Khoa",
            "experience": "3.5 năm lập trình Backend Python",
            "github_url": "https://github.com/nguyene2e",
            "is_public": True
        }
    )
    assert res_update_prf.status_code == 200
    assert res_update_prf.json()["is_public"] is True

    # BƯỚC 4: Kiểm tra đánh giá năng lực tự động (/evaluation/me)
    res_eval = client.get("/evaluation/me", headers=auth_header(token_c))
    assert res_eval.status_code == 200
    eval_data = res_eval.json()
    assert eval_data["total_score"] > 50
    assert eval_data["level"] in ["Middle", "Senior"]

    # BƯỚC 5: Đăng ký & Đăng nhập Nhà tuyển dụng
    res_reg_r = client.post("/auth/register", json={
        "email": "recruiter_e2e@example.com",
        "password": "Password123",
        "role": "recruiter"
    })
    assert res_reg_r.status_code == 200

    res_login_r = client.post("/auth/login", json={
        "email": "recruiter_e2e@example.com",
        "password": "Password123"
    })
    assert res_login_r.status_code == 200
    token_r = res_login_r.json()["token"]

    # BƯỚC 6: Nhà tuyển dụng tạo JD và gắn kỹ năng yêu cầu
    res_create_job = client.post(
        "/jobs",
        headers=auth_header(token_r),
        json={
            "title": "Senior Python Backend Engineer",
            "description": "Phát triển hệ thống microservices",
            "min_years": 2.0
        }
    )
    assert res_create_job.status_code == 200
    job_id = res_create_job.json()["id"]

    # Gắn kỹ năng bắt buộc: Python (id=1), SQL (id=3)
    res_add_s1 = client.post(
        f"/jobs/{job_id}/skills",
        headers=auth_header(token_r),
        json={"skill_id": 1, "is_required": True}
    )
    assert res_add_s1.status_code == 200

    res_add_s2 = client.post(
        f"/jobs/{job_id}/skills",
        headers=auth_header(token_r),
        json={"skill_id": 3, "is_required": True}
    )
    assert res_add_s2.status_code == 200

    # BƯỚC 7: Đối sánh AI xếp hạng ứng viên (/jobs/{id}/matches)
    res_matches = client.get(f"/jobs/{job_id}/matches", headers=auth_header(token_r))
    assert res_matches.status_code == 200
    matches_data = res_matches.json()
    assert matches_data["total"] >= 1
    top_cand = matches_data["items"][0]
    assert top_cand["full_name"] == "Nguyễn Văn E2E"
    assert top_cand["match_percent"] >= 70.0
    assert "Python" in top_cand["matched_skills"]


# ============================================================
# KIỂM THỬ BẢO MẬT VÀ PHÂN QUYỀN CHẶT CHẼ (ROLE ISOLATION)
# ============================================================

def test_e2e_security_and_role_isolation(e2e_context):
    """Kiểm tra phân quyền: Chưa đăng nhập (401/403), Sai vai trò (403), Dữ liệu người khác (404)."""
    client, db = e2e_context

    # 1. Chưa có token hợp lệ gọi API bảo vệ -> từ chối (401/403)
    assert client.get("/profiles/me", headers={"Authorization": "Bearer invalid_token"}).status_code == 401
    assert client.get("/jobs", headers={"Authorization": "Bearer invalid_token"}).status_code == 401
    assert client.get("/candidates").status_code in [401, 403]
    assert client.get("/jobs/1/matches").status_code in [401, 403]

    # 2. Tạo 1 Candidate và 2 Recruiters
    c_user = User(email="cand@test.com", password_hash="x", role="candidate")
    r1_user = User(email="rec1@test.com", password_hash="x", role="recruiter")
    r2_user = User(email="rec2@test.com", password_hash="x", role="recruiter")
    db.add_all([c_user, r1_user, r2_user])
    db.commit()

    token_c = create_token({"sub": str(c_user.id), "user_id": c_user.id, "email": c_user.email, "role": c_user.role})
    token_r1 = create_token({"sub": str(r1_user.id), "user_id": r1_user.id, "email": r1_user.email, "role": r1_user.role})
    token_r2 = create_token({"sub": str(r2_user.id), "user_id": r2_user.id, "email": r2_user.email, "role": r2_user.role})

    # Ứng viên gọi API của Nhà tuyển dụng -> 403
    assert client.get("/jobs", headers=auth_header(token_c)).status_code == 403
    assert client.post("/jobs", headers=auth_header(token_c), json={"title": "Test", "min_years": 1}).status_code == 403
    assert client.get("/candidates", headers=auth_header(token_c)).status_code == 403

    # NTD 1 tạo JD
    job1 = Job(recruiter_id=r1_user.id, title="Job NTD 1", min_years=1.0)
    db.add(job1)
    db.commit()

    # NTD 2 cố tình truy cập JD của NTD 1 -> 404
    assert client.get(f"/jobs/{job1.id}", headers=auth_header(token_r2)).status_code == 404
    assert client.get(f"/jobs/{job1.id}/matches", headers=auth_header(token_r2)).status_code == 404
