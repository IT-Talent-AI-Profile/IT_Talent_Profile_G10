import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Profile, ProfileSkill
from app.core.security import create_token

client = TestClient(app)


def headers_of(user):
    token = create_token({"sub": str(user.id), "user_id": user.id, "email": user.email, "role": user.role})
    return {"Authorization": "Bearer " + token}


def add_candidate(db, name, skill_ids, score, level="Junior", is_public=True):
    user = User(email="test_" + name + "@test.com", password_hash="x", role="candidate")
    db.add(user)
    db.commit()
    profile = Profile(user_id=user.id, full_name=name, years_experience=1.5, level=level, total_score=score, is_public=is_public)
    db.add(profile)
    db.commit()
    for skill_id in skill_ids:
        db.add(ProfileSkill(profile_id=profile.id, skill_id=skill_id, proficiency=4, years_used=2))
    db.commit()
    return profile


@pytest.fixture
def ha(data):
    return headers_of(data["a"])


@pytest.fixture
def people(db, data):
    s1 = data["skill1"].id
    s2 = data["skill2"].id
    return {
        "s1": s1,
        "s2": s2,
        "ca": add_candidate(db, "ca", [s1, s2], 50),
        "cb": add_candidate(db, "cb", [s1], 70),
        "cc": add_candidate(db, "cc", [s1, s2], 90, is_public=False),
    }


def test_chua_dang_nhap_tra_401():
    assert client.get("/candidates").status_code == 401


def test_ung_vien_goi_tra_403(db):
    ungvien = add_candidate(db, "goi", [], 10)
    user = db.query(User).filter(User.id == ungvien.user_id).first()
    assert client.get("/candidates", headers=headers_of(user)).status_code == 403
    assert client.get("/candidates/" + str(ungvien.id), headers=headers_of(user)).status_code == 403


def test_loc_hai_ky_nang_chi_ra_nguoi_co_ca_hai(ha, people):
    res = client.get("/candidates?skill_ids=" + str(people["s1"]) + "," + str(people["s2"]), headers=ha)
    assert res.status_code == 200
    assert res.json()["total"] == 1
    assert res.json()["items"][0]["full_name"] == "ca"


def test_ho_so_rieng_tu_khong_xuat_hien_va_xep_diem_giam_dan(ha, people):
    res = client.get("/candidates?skill_ids=" + str(people["s1"]), headers=ha)
    names = [item["full_name"] for item in res.json()["items"]]
    assert names == ["cb", "ca"]


def test_loc_cap_do(ha, people):
    base = "/candidates?skill_ids=" + str(people["s1"])
    assert client.get(base + "&level=Junior", headers=ha).json()["total"] == 2
    assert client.get(base + "&level=Senior", headers=ha).json()["total"] == 0
    assert client.get(base + "&level=", headers=ha).json()["total"] == 2


def test_phan_trang(db, ha, data):
    s1 = data["skill1"].id
    for i in range(11):
        add_candidate(db, "p" + str(i), [s1], 100 - i)
    base = "/candidates?skill_ids=" + str(s1)
    page1 = client.get(base + "&page=1", headers=ha).json()
    page2 = client.get(base + "&page=2", headers=ha).json()
    assert page1["total"] == 11
    assert page1["page_size"] == 10
    assert len(page1["items"]) == 10
    assert len(page2["items"]) == 1
    assert page2["items"][0]["full_name"] == "p10"
    assert client.get(base + "&page=0", headers=ha).status_code == 422


def test_skill_ids_sai_dinh_dang_khong_gay_500(ha):
    assert client.get("/candidates?skill_ids=abc", headers=ha).status_code == 422
    assert client.get("/candidates?skill_ids=1,x", headers=ha).status_code == 422


def test_xem_chi_tiet_cong_khai_va_rieng_tu(ha, people):
    res = client.get("/candidates/" + str(people["ca"].id), headers=ha)
    assert res.status_code == 200
    assert res.json()["full_name"] == "ca"
    assert len(res.json()["skills"]) == 2
    assert client.get("/candidates/" + str(people["cc"].id), headers=ha).status_code == 404
    assert client.get("/candidates/999999", headers=ha).status_code == 404