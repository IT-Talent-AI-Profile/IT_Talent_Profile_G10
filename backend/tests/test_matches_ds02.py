import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Profile, ProfileSkill, Job, JobSkill
from app.core.security import create_token

client = TestClient(app)


def headers_of(user):
    token = create_token({"sub": str(user.id), "user_id": user.id, "email": user.email, "role": user.role})
    return {"Authorization": "Bearer " + token}


def create_candidate(db, name, skill_proficiencies, years=2.0, score=75.0, level="Junior", is_public=True):
    user = User(email=f"test_{name}@test.com", password_hash="x", role="candidate")
    db.add(user)
    db.commit()
    profile = Profile(
        user_id=user.id,
        full_name=name,
        years_experience=years,
        level=level,
        total_score=score,
        is_public=is_public,
    )
    db.add(profile)
    db.commit()
    for skill_id, prof in skill_proficiencies.items():
        db.add(ProfileSkill(profile_id=profile.id, skill_id=skill_id, proficiency=prof, years_used=years))
    db.commit()
    return profile


def create_job(db, recruiter, title="Backend Dev", min_years=2.0, is_open=True, skills=None):
    job = Job(recruiter_id=recruiter.id, title=title, min_years=min_years, is_open=is_open)
    db.add(job)
    db.commit()
    if skills:
        for skill_id, is_req in skills:
            db.add(JobSkill(job_id=job.id, skill_id=skill_id, is_required=is_req))
        db.commit()
    return job


def test_matches_chua_dang_nhap_tra_401():
    res = client.get("/jobs/1/matches")
    assert res.status_code == 401


def test_matches_ung_vien_goi_tra_403(db, data):
    candidate = create_candidate(db, "cand_caller", {}, years=1.0)
    c_user = db.query(User).filter(User.id == candidate.user_id).first()
    job = create_job(db, data["a"])
    res = client.get(f"/jobs/{job.id}/matches", headers=headers_of(c_user))
    assert res.status_code == 403


def test_matches_job_khong_ton_tai_tra_404(data):
    res = client.get("/jobs/99999/matches", headers=headers_of(data["a"]))
    assert res.status_code == 404
    assert res.json()["detail"] == "Tin tuyển dụng không tồn tại"


def test_matches_job_cua_ntd_khac_tra_404(db, data):
    job_b = create_job(db, data["b"], title="Job of B")
    # NTD a gọi job của NTD b -> 404
    res = client.get(f"/jobs/{job_b.id}/matches", headers=headers_of(data["a"]))
    assert res.status_code == 404
    assert res.json()["detail"] == "Tin tuyển dụng không tồn tại"


def test_matches_job_da_dong_tra_400(db, data):
    job_closed = create_job(db, data["a"], title="Closed Job", is_open=False)
    res = client.get(f"/jobs/{job_closed.id}/matches", headers=headers_of(data["a"]))
    assert res.status_code == 400
    assert res.json()["detail"] == "Tin tuyển dụng đã đóng"


def test_matches_page_nho_hon_1_tra_422(db, data):
    job = create_job(db, data["a"])
    res = client.get(f"/jobs/{job.id}/matches?page=0", headers=headers_of(data["a"]))
    assert res.status_code == 422


def test_matches_ho_so_rieng_tu_khong_xuat_hien_va_thu_tu_giam_dan(db, data):
    s1 = data["skill1"].id
    s2 = data["skill2"].id

    job = create_job(db, data["a"], title="Fullstack Python", min_years=2.0, skills=[(s1, True), (s2, False)])

    # Candidate 1: Khớp hết 100%
    p1 = create_candidate(db, "cand_perfect", {s1: 4, s2: 4}, years=3.0, score=90.0, is_public=True)
    # Candidate 2: Khớp 1 phần
    p2 = create_candidate(db, "cand_partial", {s1: 4}, years=1.0, score=60.0, is_public=True)
    # Candidate 3: Không khớp
    p3 = create_candidate(db, "cand_none", {}, years=0.5, score=40.0, is_public=True)
    # Candidate 4: Rất giỏi nhưng is_public=False -> Không được xuất hiện
    p4 = create_candidate(db, "cand_private", {s1: 5, s2: 5}, years=5.0, score=99.0, is_public=False)

    res = client.get(f"/jobs/{job.id}/matches?page=1", headers=headers_of(data["a"]))
    assert res.status_code == 200
    data_res = res.json()

    assert data_res["job"] == "Fullstack Python"
    assert data_res["page"] == 1
    assert data_res["page_size"] == 10
    
    returned_ids = [item["id"] for item in data_res["items"]]
    # Hồ sơ riêng tư p4 KHÔNG được xuất hiện
    assert p4.id not in returned_ids

    # Thứ tự phải giảm dần theo match_percent
    percents = [item["match_percent"] for item in data_res["items"]]
    assert percents == sorted(percents, reverse=True)
    assert percents[0] == 100.0


def test_matches_phan_trang_page_2(db, data):
    s1 = data["skill1"].id
    job = create_job(db, data["a"], title="Paginated Job", min_years=1.0, skills=[(s1, True)])

    # Tạo 12 ứng viên công khai
    for i in range(12):
        create_candidate(db, f"cand_page_{i}", {s1: 3}, years=2.0, score=50.0 + i, is_public=True)

    res_p1 = client.get(f"/jobs/{job.id}/matches?page=1", headers=headers_of(data["a"]))
    assert res_p1.status_code == 200
    assert len(res_p1.json()["items"]) == 10
    assert res_p1.json()["total"] >= 12

    res_p2 = client.get(f"/jobs/{job.id}/matches?page=2", headers=headers_of(data["a"]))
    assert res_p2.status_code == 200
    assert len(res_p2.json()["items"]) >= 2
    # Bản ghi trang 2 không trùng với trang 1
    p1_ids = {x["id"] for x in res_p1.json()["items"]}
    p2_ids = {x["id"] for x in res_p2.json()["items"]}
    assert p1_ids.isdisjoint(p2_ids)
