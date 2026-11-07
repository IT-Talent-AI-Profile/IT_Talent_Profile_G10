from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db


def test_login_token_authenticates_current_user_and_appears_in_openapi(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            register = client.post(
                "/auth/register",
                json={
                    "email": "test_auth_candidate@test.com",
                    "password": "password123",
                    "full_name": "Test Candidate",
                    "role": "candidate",
                },
            )
            assert register.status_code == 200

            login = client.post(
                "/auth/login",
                json={
                    "email": "test_auth_candidate@test.com",
                    "password": "password123",
                },
            )
            assert login.status_code == 200
            token = login.json()["token"]

            response = client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200
            assert response.json()["email"] == "test_auth_candidate@test.com"
            assert response.json()["role"] == "candidate"

            schema = client.get("/openapi.json").json()
            assert "HTTPBearer" in schema["components"]["securitySchemes"]
            assert "/auth/me" in schema["paths"]
    finally:
        app.dependency_overrides.clear()


def test_candidate_endpoint_rejects_recruiter_token(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            register = client.post(
                "/auth/register",
                json={
                    "email": "test_auth_recruiter@test.com",
                    "password": "password123",
                    "role": "recruiter",
                },
            )
            assert register.status_code == 200

            login = client.post(
                "/auth/login",
                json={
                    "email": "test_auth_recruiter@test.com",
                    "password": "password123",
                },
            )
            assert login.status_code == 200
            token = login.json()["token"]

            response = client.get(
                "/candidate/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_recruiter_endpoint_rejects_candidate_token(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            register = client.post(
                "/auth/register",
                json={
                    "email": "test_auth_candidate_role@test.com",
                    "password": "password123",
                    "full_name": "Test Candidate",
                    "role": "candidate",
                },
            )
            assert register.status_code == 200

            login = client.post(
                "/auth/login",
                json={
                    "email": "test_auth_candidate_role@test.com",
                    "password": "password123",
                },
            )
            assert login.status_code == 200
            token = login.json()["token"]

            response = client.get(
                "/recruiter/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()
