import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.models import Job, JobSkill, User
from app.schemas.job import JobIn, JobSkillIn
from app.core.security import create_token
from app.services.job_service import (
    create_job,
    list_jobs,
    get_job,
    update_job,
    delete_job,
    set_status,
    add_skill,
    remove_skill,
    find_job,
)

# ============================================================
# PHẦN 1: UNIT TESTS CHO SERVICE LAYER (JD-01, JD-02)
# ============================================================

def test_create_and_get_job(db, data):
    """Kiểm tra tạo JD mới và đọc lại thông tin đúng như yêu cầu DoD."""
    recruiter_a = data["a"]
    job_in = JobIn(
        title="Senior Python Backend Engineer",
        description="Tuyển lập trình viên Python phát triển hệ thống phân tán",
        min_years=3.5,
    )

    job_dict = create_job(db, recruiter_a.id, job_in)

    assert job_dict["id"] is not None
    assert job_dict["title"] == "Senior Python Backend Engineer"
    assert job_dict["description"] == "Tuyển lập trình viên Python phát triển hệ thống phân tán"
    assert job_dict["min_years"] == 3.5
    assert job_dict["is_open"] is True
    assert job_dict["skills"] == []

    fetched = get_job(db, recruiter_a.id, job_dict["id"])
    assert fetched["id"] == job_dict["id"]
    assert fetched["title"] == job_dict["title"]


def test_list_jobs_isolation(db, data):
    """Kiểm tra tính cô lập: NTD chỉ thấy danh sách JD của chính mình."""
    recruiter_a = data["a"]
    recruiter_b = data["b"]

    create_job(db, recruiter_a.id, JobIn(title="JD A1", description="", min_years=1))
    create_job(db, recruiter_a.id, JobIn(title="JD A2", description="", min_years=2))
    create_job(db, recruiter_b.id, JobIn(title="JD B1", description="", min_years=3))

    jobs_a = list_jobs(db, recruiter_a.id)
    jobs_b = list_jobs(db, recruiter_b.id)

    titles_a = [j["title"] for j in jobs_a]
    titles_b = [j["title"] for j in jobs_b]

    assert "JD A1" in titles_a
    assert "JD A2" in titles_a
    assert "JD B1" not in titles_a

    assert "JD B1" in titles_b
    assert "JD A1" not in titles_b
    assert "JD A2" not in titles_b


def test_recruiter_cannot_access_other_recruiters_job(db, data):
    """Kiểm tra NTD A không thể xem hoặc thao tác trên JD của NTD B (báo 404)."""
    recruiter_a = data["a"]
    recruiter_b = data["b"]

    job_a = create_job(db, recruiter_a.id, JobIn(title="Bí mật của A", description="", min_years=1))

    with pytest.raises(HTTPException) as exc_info:
        get_job(db, recruiter_b.id, job_a["id"])
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Không tìm thấy JD"


def test_update_job(db, data):
    """Kiểm tra cập nhật thông tin JD (tiêu đề, mô tả, số năm kinh nghiệm)."""
    recruiter_a = data["a"]
    job = create_job(db, recruiter_a.id, JobIn(title="Junior Python", description="Mô tả cũ", min_years=1.0))

    update_in = JobIn(title="Middle Python Engineer", description="Mô tả mới đã cập nhật", min_years=3.0)
    updated = update_job(db, recruiter_a.id, job["id"], update_in)

    assert updated["id"] == job["id"]
    assert updated["title"] == "Middle Python Engineer"
    assert updated["description"] == "Mô tả mới đã cập nhật"
    assert updated["min_years"] == 3.0


def test_set_status_two_way(db, data):
    """Kiểm tra đóng/mở trạng thái JD được cả hai chiều."""
    recruiter_a = data["a"]
    job = create_job(db, recruiter_a.id, JobIn(title="JD Test Status", description="", min_years=1))

    # Đóng JD
    closed = set_status(db, recruiter_a.id, job["id"], is_open=False)
    assert closed["is_open"] is False

    # Mở lại JD
    reopened = set_status(db, recruiter_a.id, job["id"], is_open=True)
    assert reopened["is_open"] is True


def test_add_and_update_skill(db, data):
    """Kiểm tra gắn kỹ năng vào JD: nếu đã có thì cập nhật is_required chứ không tạo dòng trùng."""
    recruiter_a = data["a"]
    skill1 = data["skill1"]
    job = create_job(db, recruiter_a.id, JobIn(title="JD Python & Cloud", description="", min_years=2))

    res1 = add_skill(db, recruiter_a.id, job["id"], JobSkillIn(skill_id=skill1.id, is_required=True))
    assert len(res1["skills"]) == 1
    assert res1["skills"][0]["skill_id"] == skill1.id
    assert res1["skills"][0]["is_required"] is True

    res2 = add_skill(db, recruiter_a.id, job["id"], JobSkillIn(skill_id=skill1.id, is_required=False))
    assert len(res2["skills"]) == 1
    assert res2["skills"][0]["skill_id"] == skill1.id
    assert res2["skills"][0]["is_required"] is False


def test_add_nonexistent_skill_raises_404(db, data):
    """Kiểm tra gắn kỹ năng không tồn tại báo lỗi 404."""
    recruiter_a = data["a"]
    job = create_job(db, recruiter_a.id, JobIn(title="JD Test 404", description="", min_years=1))

    with pytest.raises(HTTPException) as exc_info:
        add_skill(db, recruiter_a.id, job["id"], JobSkillIn(skill_id=999999, is_required=True))
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Kỹ năng không tồn tại"


def test_remove_skill(db, data):
    """Kiểm tra gỡ kỹ năng khỏi JD thành công."""
    recruiter_a = data["a"]
    skill1 = data["skill1"]
    job = create_job(db, recruiter_a.id, JobIn(title="JD Test Remove Skill", description="", min_years=1))

    add_skill(db, recruiter_a.id, job["id"], JobSkillIn(skill_id=skill1.id, is_required=True))
    res = remove_skill(db, recruiter_a.id, job["id"], skill1.id)
    assert len(res["skills"]) == 0


def test_remove_unattached_skill_raises_404(db, data):
    """Kiểm tra gỡ kỹ năng chưa được gắn vào JD báo lỗi 404."""
    recruiter_a = data["a"]
    skill2 = data["skill2"]
    job = create_job(db, recruiter_a.id, JobIn(title="JD Test Unattached", description="", min_years=1))

    with pytest.raises(HTTPException) as exc_info:
        remove_skill(db, recruiter_a.id, job["id"], skill2.id)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "JD chưa có kỹ năng này"


def test_delete_job_cascades_skills(db, data):
    """Kiểm tra xóa JD thì các kỹ năng trong job_skills liên quan bị xóa theo (CASCADE)."""
    recruiter_a = data["a"]
    skill1 = data["skill1"]
    skill2 = data["skill2"]

    job = create_job(db, recruiter_a.id, JobIn(title="JD Sắp Bị Xóa", description="", min_years=2))
    job_id = job["id"]

    add_skill(db, recruiter_a.id, job_id, JobSkillIn(skill_id=skill1.id, is_required=True))
    add_skill(db, recruiter_a.id, job_id, JobSkillIn(skill_id=skill2.id, is_required=False))

    count_before = db.query(JobSkill).filter(JobSkill.job_id == job_id).count()
    assert count_before == 2

    delete_job(db, recruiter_a.id, job_id)

    with pytest.raises(HTTPException) as exc_info:
        find_job(db, recruiter_a.id, job_id)
    assert exc_info.value.status_code == 404

    count_after = db.query(JobSkill).filter(JobSkill.job_id == job_id).count()
    assert count_after == 0


# ============================================================
# PHẦN 2: INTEGRATION TESTS CHO REST API ENDPOINTS (JD-03)
# ============================================================

client = TestClient(app)


def headers_of(user):
    token = create_token({"sub": str(user.id), "user_id": user.id, "email": user.email, "role": user.role})
    return {"Authorization": "Bearer " + token}


@pytest.fixture
def ha(data):
    return headers_of(data["a"])


@pytest.fixture
def hb(data):
    return headers_of(data["b"])


@pytest.fixture
def hc(db):
    ungvien = User(email="test_c@test.com", password_hash="x", role="candidate")
    db.add(ungvien)
    db.commit()
    return headers_of(ungvien)


def tao_jd(headers, title="Backend Junior"):
    res = client.post("/jobs", json={"title": title, "description": "Mô tả", "min_years": 1}, headers=headers)
    assert res.status_code == 200
    return res.json()


def test_chua_dang_nhap_tra_401():
    assert client.get("/jobs").status_code == 401
    assert client.post("/jobs", json={"title": "x"}).status_code == 401


def test_ung_vien_goi_api_ntd_tra_403(hc):
    assert client.get("/jobs", headers=hc).status_code == 403
    assert client.post("/jobs", json={"title": "x"}, headers=hc).status_code == 403


def test_du_lieu_sai_tra_422(ha):
    assert client.post("/jobs", json={"title": ""}, headers=ha).status_code == 422
    assert client.post("/jobs", json={"title": "x", "min_years": -1}, headers=ha).status_code == 422


def test_tao_xem_sua_xoa(ha):
    job = tao_jd(ha)
    assert job["is_open"] is True
    assert client.get("/jobs/" + str(job["id"]), headers=ha).json()["title"] == "Backend Junior"
    res = client.put("/jobs/" + str(job["id"]), json={"title": "Backend Middle", "description": "Mới", "min_years": 2}, headers=ha)
    assert res.json()["title"] == "Backend Middle"
    assert res.json()["min_years"] == 2
    assert client.delete("/jobs/" + str(job["id"]), headers=ha).json() == {"message": "Đã xóa JD"}
    assert client.get("/jobs/" + str(job["id"]), headers=ha).status_code == 404


def test_ntd_khac_khong_doc_duoc_jd_tra_404(ha, hb):
    job = tao_jd(ha)
    url = "/jobs/" + str(job["id"])
    assert client.get(url, headers=hb).status_code == 404
    assert client.put(url, json={"title": "x"}, headers=hb).status_code == 404
    assert client.delete(url, headers=hb).status_code == 404
    assert client.patch(url + "/status", json={"is_open": False}, headers=hb).status_code == 404
    assert client.get("/jobs", headers=hb).json() == []


def test_dong_mo_jd(ha):
    job = tao_jd(ha)
    url = "/jobs/" + str(job["id"]) + "/status"
    assert client.patch(url, json={"is_open": False}, headers=ha).json()["is_open"] is False
    assert client.patch(url, json={"is_open": True}, headers=ha).json()["is_open"] is True


def test_gan_va_go_ky_nang(ha, data):
    job = tao_jd(ha)
    base = "/jobs/" + str(job["id"]) + "/skills"
    skill_id = data["skill1"].id
    res = client.post(base, json={"skill_id": skill_id, "is_required": True}, headers=ha)
    assert len(res.json()["skills"]) == 1
    res = client.post(base, json={"skill_id": skill_id, "is_required": False}, headers=ha)
    assert len(res.json()["skills"]) == 1
    assert res.json()["skills"][0]["is_required"] is False
    assert client.post(base, json={"skill_id": 999999, "is_required": True}, headers=ha).status_code == 404
    res = client.delete(base + "/" + str(skill_id), headers=ha)
    assert res.json()["skills"] == []
    assert client.delete(base + "/" + str(skill_id), headers=ha).status_code == 404
