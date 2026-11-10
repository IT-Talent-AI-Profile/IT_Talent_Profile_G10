import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User
from app.core.security import create_token

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