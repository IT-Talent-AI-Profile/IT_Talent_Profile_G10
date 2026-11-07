import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_token
from app.models.user import User
from app.models.profile import Profile
from app.models.skill import Skill

client = TestClient(app)


@pytest.fixture
def auth_headers(db):
    """Tạo user candidate và user recruiter mẫu để test phân quyền và API."""
    # 1. Candidate
    cand_user = db.query(User).filter(User.email == "test_cand_profile@test.com").first()
    if not cand_user:
        cand_user = User(email="test_cand_profile@test.com", password_hash="hash", role="candidate")
        db.add(cand_user)
        db.commit()
        db.refresh(cand_user)

    cand_profile = db.query(Profile).filter(Profile.user_id == cand_user.id).first()
    if not cand_profile:
        cand_profile = Profile(
            user_id=cand_user.id,
            full_name="Nguyễn Văn Hồ Sơ",
            desired_position="Backend Developer",
            years_experience=2.0,
            is_public=False
        )
        db.add(cand_profile)
        db.commit()

    # 2. Recruiter
    rec_user = db.query(User).filter(User.email == "test_rec_profile@test.com").first()
    if not rec_user:
        rec_user = User(email="test_rec_profile@test.com", password_hash="hash", role="recruiter")
        db.add(rec_user)
        db.commit()
        db.refresh(rec_user)

    cand_token = create_token({"user_id": cand_user.id, "sub": str(cand_user.id), "role": "candidate"})
    rec_token = create_token({"user_id": rec_user.id, "sub": str(rec_user.id), "role": "recruiter"})

    return {
        "candidate": {"Authorization": f"Bearer {cand_token}"},
        "recruiter": {"Authorization": f"Bearer {rec_token}"},
        "cand_user": cand_user,
    }


# ==========================================
# TEST TASK [HS-01]: Xem và sửa hồ sơ cá nhân
# ==========================================
def test_get_profile_me_success(auth_headers):
    res = client.get("/profiles/me", headers=auth_headers["candidate"])
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "Nguyễn Văn Hồ Sơ"
    assert "skills" in data


def test_get_profile_me_recruiter_forbidden(auth_headers):
    # NTD gọi API hồ sơ ứng viên -> 403
    res = client.get("/profiles/me", headers=auth_headers["recruiter"])
    assert res.status_code == 403
    assert "chỉ dành cho ứng viên" in res.json()["detail"].lower()


def test_get_profile_me_unauthorized():
    # Không có token -> 401 hoặc 403
    res = client.get("/profiles/me")
    assert res.status_code in (401, 403)


def test_update_profile_me_success(auth_headers):
    update_data = {
        "full_name": "Nguyễn Văn Cập Nhật",
        "desired_position": "Senior Backend Developer",
        "years_experience": 3.5,
        "education": "Đại học Bách Khoa",
        "experience": "3.5 năm kinh nghiệm Python, FastAPI",
        "github_url": "https://github.com/nguyencapnhat",
        "is_public": True
    }
    res = client.put("/profiles/me", json=update_data, headers=auth_headers["candidate"])
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "Nguyễn Văn Cập Nhật"
    assert data["years_experience"] == 3.5
    assert data["is_public"] is True

    # Kiểm tra GET lại thấy đúng dữ liệu
    get_res = client.get("/profiles/me", headers=auth_headers["candidate"])
    assert get_res.status_code == 200
    assert get_res.json()["desired_position"] == "Senior Backend Developer"


def test_update_profile_negative_years(auth_headers):
    # years_experience âm -> 422
    update_data = {
        "full_name": "Nguyễn Văn Lỗi",
        "years_experience": -1.0,
        "is_public": False
    }
    res = client.put("/profiles/me", json=update_data, headers=auth_headers["candidate"])
    assert res.status_code == 422


# ==========================================
# TEST TASK [HS-02]: Danh mục kỹ năng & Profile Skills
# ==========================================
def test_get_skills_authenticated(auth_headers):
    # Cả candidate và recruiter đều gọi được /skills
    res_cand = client.get("/skills", headers=auth_headers["candidate"])
    assert res_cand.status_code == 200
    skills = res_cand.json()
    assert len(skills) > 0
    assert "group" in skills[0]

    res_rec = client.get("/skills", headers=auth_headers["recruiter"])
    assert res_rec.status_code == 200


def test_get_skills_unauthorized():
    res = client.get("/skills")
    assert res.status_code in (401, 403)


def test_add_and_update_profile_skill(auth_headers, db):
    # Lấy 1 skill thật trong DB
    skill = db.query(Skill).first()
    assert skill is not None

    # 1. Thêm mới kỹ năng
    add_data = {
        "skill_id": skill.id,
        "proficiency": 4,
        "years_used": 2.5
    }
    res = client.post("/profiles/me/skills", json=add_data, headers=auth_headers["candidate"])
    assert res.status_code == 200
    skills = res.json()["skills"]
    matched = [s for s in skills if s["skill_id"] == skill.id]
    assert len(matched) == 1
    assert matched[0]["proficiency"] == 4
    assert matched[0]["years_used"] == 2.5

    # 2. Thêm lại cùng skill_id -> cập nhật (Upsert), không tạo dòng trùng
    update_data = {
        "skill_id": skill.id,
        "proficiency": 5,
        "years_used": 3.0
    }
    res_up = client.post("/profiles/me/skills", json=update_data, headers=auth_headers["candidate"])
    assert res_up.status_code == 200
    skills_up = res_up.json()["skills"]
    matched_up = [s for s in skills_up if s["skill_id"] == skill.id]
    assert len(matched_up) == 1  # Không bị nhân đôi
    assert matched_up[0]["proficiency"] == 5
    assert matched_up[0]["years_used"] == 3.0


def test_add_profile_skill_invalid(auth_headers):
    # skill_id không tồn tại -> 404
    res_404 = client.post("/profiles/me/skills", json={
        "skill_id": 99999,
        "proficiency": 4,
        "years_used": 1.0
    }, headers=auth_headers["candidate"])
    assert res_404.status_code == 404

    # proficiency = 7 -> 422
    res_422 = client.post("/profiles/me/skills", json={
        "skill_id": 1,
        "proficiency": 7,
        "years_used": 1.0
    }, headers=auth_headers["candidate"])
    assert res_422.status_code == 422


def test_delete_profile_skill(auth_headers, db):
    skill = db.query(Skill).first()

    # Thêm trước để xóa
    client.post("/profiles/me/skills", json={
        "skill_id": skill.id,
        "proficiency": 3,
        "years_used": 1.0
    }, headers=auth_headers["candidate"])

    # Xóa kỹ năng
    del_res = client.delete(f"/profiles/me/skills/{skill.id}", headers=auth_headers["candidate"])
    assert del_res.status_code == 200
    skills_after = del_res.json()["skills"]
    assert not any(s["skill_id"] == skill.id for s in skills_after)

    # Xóa lại lần nữa -> 404
    del_again = client.delete(f"/profiles/me/skills/{skill.id}", headers=auth_headers["candidate"])
    assert del_again.status_code == 404
