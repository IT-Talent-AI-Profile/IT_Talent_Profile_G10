import pytest
from fastapi import HTTPException
from app.models import Job, JobSkill
from app.schemas.job import JobIn, JobSkillIn
from app.services.job_service import (
    create_job,
    list_jobs,
    get_job,
    update_job,
    delete_job,
    set_status,
    add_skill,
    remove_skill,
    find_job
)


def test_create_and_get_job(db, data):
    """Kiểm tra tạo JD mới và đọc lại thông tin đúng như yêu cầu DoD."""
    recruiter_a = data["a"]
    job_in = JobIn(
        title="Senior Python Backend Engineer",
        description="Tuyển lập trình viên Python phát triển hệ thống phân tán",
        min_years=3.5
    )

    job_dict = create_job(db, recruiter_a.id, job_in)

    assert job_dict["id"] is not None
    assert job_dict["title"] == "Senior Python Backend Engineer"
    assert job_dict["description"] == "Tuyển lập trình viên Python phát triển hệ thống phân tán"
    assert job_dict["min_years"] == 3.5
    assert job_dict["is_open"] is True
    assert job_dict["skills"] == []

    # Đọc lại thông tin qua get_job
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

    # 1. Gắn kỹ năng với is_required = True
    res1 = add_skill(db, recruiter_a.id, job["id"], JobSkillIn(skill_id=skill1.id, is_required=True))
    assert len(res1["skills"]) == 1
    assert res1["skills"][0]["skill_id"] == skill1.id
    assert res1["skills"][0]["is_required"] is True

    # 2. Gắn lại cùng kỹ năng với is_required = False -> Phải cập nhật, không tăng số lượng
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

    # Xác nhận trong DB có 2 dòng job_skills
    count_before = db.query(JobSkill).filter(JobSkill.job_id == job_id).count()
    assert count_before == 2

    # Xóa JD
    delete_job(db, recruiter_a.id, job_id)

    # Kiểm tra job không còn
    with pytest.raises(HTTPException) as exc_info:
        find_job(db, recruiter_a.id, job_id)
    assert exc_info.value.status_code == 404

    # Kiểm tra job_skills liên quan bị xóa theo hoàn toàn
    count_after = db.query(JobSkill).filter(JobSkill.job_id == job_id).count()
    assert count_after == 0
