from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_candidate
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Profile, Skill, User
from app.services import cv_service
from app.services.ai_client import settings as ai_settings
from tests.test_pdf_parser import create_blank_pdf, create_text_pdf


@pytest.fixture
def cv_test_context(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSession()

    candidate = User(
        email="cv_candidate@test.local",
        password_hash="test-hash",
        role="candidate",
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    profile = Profile(user_id=candidate.id, full_name="CV Test Candidate")
    python = Skill(name="Python", skill_group="Backend")
    fastapi = Skill(name="FastAPI", skill_group="Backend")
    db.add_all([profile, python, fastapi])
    db.commit()
    db.refresh(profile)
    db.refresh(python)
    db.refresh(fastapi)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_candidate] = lambda: candidate
    monkeypatch.setattr(cv_service, "UPLOAD_DIR", Path(tmp_path) / "private_uploads")
    monkeypatch.setattr(ai_settings, "AI_MODE", "mock")
    monkeypatch.setattr(ai_settings, "AI_API_KEY", "")

    yield TestClient(app), db, candidate, profile, python, fastapi

    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_cv_upload_get_and_confirm_flow(cv_test_context):
    client, db, candidate, profile, python, fastapi = cv_test_context
    pdf = create_text_pdf(["Backend Developer", "Experience with Python and FastAPI"])

    upload = client.post(
        "/cv/upload",
        files={"file": ("resume.pdf", pdf, "application/pdf")},
    )
    assert upload.status_code == 200, upload.text
    payload = upload.json()
    assert payload["status"] == "success"
    assert payload["cv_id"] > 0
    assert payload["result"]["years_experience"] == 1.0
    assert payload["result"]["skills"]

    cv_id = payload["cv_id"]
    get_result = client.get(f"/cv/{cv_id}")
    assert get_result.status_code == 200
    assert get_result.json()["status"] == "success"

    selected_skill = payload["result"]["skills"][0]
    confirm = client.post(
        f"/cv/{cv_id}/confirm",
        json={
            "skills": [{
                "skill_id": selected_skill["skill_id"],
                "proficiency": 4,
                "years_used": 2.5,
            }],
            "years_experience": 2.5,
            "education": "Bachelor of Information Technology",
            "experience": "Backend Developer",
        },
    )
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["years_experience"] == 2.5
    assert confirm.json()["education"] == "Bachelor of Information Technology"
    assert len(confirm.json()["skills"]) == 1

    cv_record = db.query(cv_service.CvFile).filter_by(id=cv_id).one()
    assert cv_record.status == "confirmed"
    stored_file = cv_service.UPLOAD_DIR / Path(cv_record.file_path).name
    assert stored_file.exists()


def test_cv_upload_rejects_wrong_extension(cv_test_context):
    client, *_ = cv_test_context
    response = client.post(
        "/cv/upload",
        files={"file": ("resume.docx", b"not a pdf", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_cv_upload_rejects_file_over_5mb(cv_test_context):
    client, *_ = cv_test_context
    content = b"%PDF-1.4\n" + b"x" * (5 * 1024 * 1024)
    response = client.post(
        "/cv/upload",
        files={"file": ("large.pdf", content, "application/pdf")},
    )
    assert response.status_code == 413


def test_cv_upload_records_pdf_without_text_as_failed(cv_test_context):
    client, db, *_ = cv_test_context
    response = client.post(
        "/cv/upload",
        files={"file": ("scanned.pdf", create_blank_pdf(), "application/pdf")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "failed"
    assert "Không trích xuất được văn bản" in body["error_message"]


def test_cv_confirm_rejects_duplicate_skills(cv_test_context):
    client, _, _, _, python, _ = cv_test_context
    pdf = create_text_pdf(["Python Developer"])
    upload = client.post("/cv/upload", files={"file": ("resume.pdf", pdf, "application/pdf")})
    assert upload.status_code == 200
    cv_id = upload.json()["cv_id"]
    response = client.post(
        f"/cv/{cv_id}/confirm",
        json={
            "skills": [
                {"skill_id": python.id, "proficiency": 3, "years_used": 1},
                {"skill_id": python.id, "proficiency": 4, "years_used": 2},
            ],
            "years_experience": 2,
        },
    )
    assert response.status_code == 422


def test_cv_result_is_private_to_owning_candidate(cv_test_context):
    client, db, _, _, _, _ = cv_test_context
    upload = client.post(
        "/cv/upload",
        files={"file": ("resume.pdf", create_text_pdf(["Python Developer"]), "application/pdf")},
    )
    assert upload.status_code == 200
    cv_id = upload.json()["cv_id"]

    other_candidate = User(
        email="other_candidate@test.local",
        password_hash="test-hash",
        role="candidate",
    )
    db.add(other_candidate)
    db.commit()
    app.dependency_overrides[get_candidate] = lambda: other_candidate

    response = client.get(f"/cv/{cv_id}")
    assert response.status_code == 404
