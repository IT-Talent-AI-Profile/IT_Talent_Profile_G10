from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.api.dependencies import get_candidate
from app.models import User, Profile, Skill, ProfileSkill
from app.services import cv_service, evaluation_service
from app.services.ai_client import settings as ai_settings
from tests.test_pdf_parser import create_blank_pdf, create_text_pdf


@pytest.fixture
def kt02_context(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSession()

    candidate = User(
        email="kt02_candidate@test.local",
        password_hash="test-hash",
        role="candidate",
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    profile = Profile(user_id=candidate.id, full_name="KT02 Test Candidate")
    python = Skill(name="Python", skill_group="Backend")
    react = Skill(name="React", skill_group="Frontend")
    docker = Skill(name="Docker", skill_group="DevOps")
    db.add_all([profile, python, react, docker])
    db.commit()
    db.refresh(profile)
    db.refresh(python)
    db.refresh(react)
    db.refresh(docker)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_candidate] = lambda: candidate
    monkeypatch.setattr(cv_service, "UPLOAD_DIR", Path(tmp_path) / "private_uploads")
    monkeypatch.setattr(ai_settings, "AI_MODE", "mock")
    monkeypatch.setattr(ai_settings, "AI_API_KEY", "")

    yield TestClient(app), db, candidate, profile, python, react, docker

    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


# ============================================================
# PHẦN 1: KIỂM THỬ MODULE CV (THEO DOD KT-02)
# ============================================================

def test_tc_cv_01_txt_renamed_to_pdf(kt02_context):
    """File .txt đổi đuôi thành .pdf bị từ chối với HTTP 400 do không phải cấu trúc PDF hợp lệ."""
    client, *_ = kt02_context
    txt_content = b"This is plain text pretending to be a pdf file."
    res = client.post(
        "/cv/upload",
        files={"file": ("fake.pdf", txt_content, "application/pdf")},
    )
    assert res.status_code == 400
    assert "PDF" in res.json()["detail"]


def test_tc_cv_02_file_over_5mb(kt02_context):
    """File dung lượng trên 5 MB bị từ chối với mã lỗi 413 Payload Too Large."""
    client, *_ = kt02_context
    large_pdf = b"%PDF-1.4\n" + b"x" * (5 * 1024 * 1024 + 10)
    res = client.post(
        "/cv/upload",
        files={"file": ("large_resume.pdf", large_pdf, "application/pdf")},
    )
    assert res.status_code == 413


def test_tc_cv_03_scanned_pdf_without_text(kt02_context):
    """PDF ảnh quét (không có text stream) được ghi nhận trạng thái failed với thông báo rõ ràng."""
    client, *_ = kt02_context
    res = client.post(
        "/cv/upload",
        files={"file": ("scanned_resume.pdf", create_blank_pdf(), "application/pdf")},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "failed"
    assert "Không trích xuất được văn bản" in body["error_message"]


def test_tc_cv_04_ai_error_handling(kt02_context, monkeypatch):
    """Khi AI gặp lỗi ngoại lệ hoặc timeout, hệ thống bắt lỗi an toàn và ghi nhận status failed."""
    client, *_ = kt02_context

    def raise_ai_error(*args, **kwargs):
        raise RuntimeError("AI API Connection Timeout")

    monkeypatch.setattr(cv_service, "extract_cv", raise_ai_error)
    pdf = create_text_pdf(["Python Backend Developer"])
    res = client.post(
        "/cv/upload",
        files={"file": ("cv.pdf", pdf, "application/pdf")},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "failed"
    assert "AI API Connection Timeout" in body["error_message"]


def test_tc_cv_05_view_other_candidate_cv_raises_404(kt02_context):
    """Tính cô lập dữ liệu: Ứng viên khác không thể xem kết quả CV của người dùng sở hữu (404)."""
    client, db, _, _, _, _, _ = kt02_context
    pdf = create_text_pdf(["Python Developer"])
    res = client.post("/cv/upload", files={"file": ("cv.pdf", pdf, "application/pdf")})
    assert res.status_code == 200
    cv_id = res.json()["cv_id"]

    other_user = User(email="other_user@test.local", password_hash="pass", role="candidate")
    db.add(other_user)
    db.commit()
    profile_other = Profile(user_id=other_user.id, full_name="Other Candidate")
    db.add(profile_other)
    db.commit()

    app.dependency_overrides[get_candidate] = lambda: other_user
    res_other = client.get(f"/cv/{cv_id}")
    assert res_other.status_code == 404
    assert "Không tìm thấy CV" in res_other.json()["detail"]


def test_tc_cv_06_confirm_twice(kt02_context):
    """Xác nhận kết quả CV 2 lần: lần 2 vẫn cập nhật an toàn hoặc không gây lỗi hệ thống."""
    client, _, _, _, python, _, _ = kt02_context
    pdf = create_text_pdf(["Python Developer with FastAPI"])
    upload = client.post("/cv/upload", files={"file": ("cv.pdf", pdf, "application/pdf")})
    cv_id = upload.json()["cv_id"]

    payload = {
        "skills": [{"skill_id": python.id, "proficiency": 4, "years_used": 2.0}],
        "years_experience": 2.0,
        "education": "Đại học CNTT",
        "experience": "Lập trình viên",
    }
    res1 = client.post(f"/cv/{cv_id}/confirm", json=payload)
    assert res1.status_code == 200

    # Xác nhận lần 2
    res2 = client.post(f"/cv/{cv_id}/confirm", json=payload)
    assert res2.status_code == 200
    assert res2.json()["total_score"] > 0


# ============================================================
# PHẦN 2: KIỂM THỬ ĐÁNH GIÁ NĂNG LỰC (THEO DOD KT-02)
# ============================================================

def test_tc_eval_01_5_years_75_score():
    """(5 năm, 75 điểm) -> Xếp cấp độ Senior chuẩn xác."""
    assert evaluation_service.determine_level(5.0, 75.0) == "Senior"


def test_tc_eval_02_4_9_years_90_score():
    """(4.9 năm, 90 điểm) -> Dù điểm rất cao nhưng chưa đủ 5 năm kinh nghiệm -> Xếp cấp độ Middle."""
    assert evaluation_service.determine_level(4.9, 90.0) == "Middle"


def test_tc_eval_03_profile_without_skills():
    """Hồ sơ không có kỹ năng -> Điểm tổng = 0, xếp cấp độ Intern."""
    profile = Profile(user_id=1, full_name="No Skills", years_experience=0)
    profile.skills = []
    result = evaluation_service.evaluate_profile(profile)
    assert result.total_score == 0
    assert result.level == "Intern"
    assert result.groups == {}


def test_tc_eval_04_single_skill_group():
    """Hồ sơ chỉ có kỹ năng thuộc 1 nhóm chuyên môn -> Tính điểm trung bình nhóm đúng."""
    python = Skill(id=1, name="Python", skill_group="Backend")
    ps = ProfileSkill(skill=python, proficiency=3, years_used=1.0)
    # 3 * 12 + 1 * 8 = 36 + 8 = 44 điểm
    profile = Profile(user_id=1, full_name="Single Group", years_experience=1.0)
    profile.skills = [ps]
    result = evaluation_service.evaluate_profile(profile)
    assert result.groups == {"Backend": 44.0}
    assert result.total_score == 44.0
    assert result.level == "Junior"


def test_tc_eval_05_multiple_skill_groups():
    """Hồ sơ có kỹ năng thuộc nhiều nhóm (Backend + Frontend) -> Điểm tổng bằng trung bình các nhóm."""
    py = Skill(id=1, name="Python", skill_group="Backend")
    rc = Skill(id=2, name="React", skill_group="Frontend")
    ps1 = ProfileSkill(skill=py, proficiency=4, years_used=2.5)  # 4*12 + 2.5*8 = 48 + 20 = 68
    ps2 = ProfileSkill(skill=rc, proficiency=4, years_used=2.5)  # 68
    profile = Profile(user_id=1, full_name="Multi Group", years_experience=3.0)
    profile.skills = [ps1, ps2]
    result = evaluation_service.evaluate_profile(profile)
    assert result.groups["Backend"] == 68.0
    assert result.groups["Frontend"] == 68.0
    assert result.total_score == 68.0
    assert result.level == "Middle"


def test_tc_eval_06_proficiency_5_and_5_years_reaches_100():
    """Proficiency 5 và 5 năm kinh nghiệm -> Đạt trọn vẹn 100 điểm."""
    score = evaluation_service.calculate_skill_score(proficiency=5, years_used=5.0)
    assert score == 100.0


def test_tc_eval_07_years_used_greater_than_5_capped_at_100():
    """years_used lớn hơn 5 (vd: 8 năm) với proficiency 5 -> Giới hạn trần ở 100 điểm, không vượt quá thang 100."""
    score = evaluation_service.calculate_skill_score(proficiency=5, years_used=8.0)
    assert score == 100.0
