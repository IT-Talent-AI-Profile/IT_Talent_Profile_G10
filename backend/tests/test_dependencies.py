
import pytest

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import (
    get_current_user,
    get_candidate,
    get_recruiter
)
from app.core.security import create_token
from app.models.user import User


def make_credentials(token):
    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token
    )


def make_token(user):
    return create_token({
        "sub": str(user.id),
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    })


def test_missing_token(db):
    with pytest.raises(HTTPException) as exc:
        get_current_user(None, db)

    assert exc.value.status_code == 401


def test_invalid_token(db):
    with pytest.raises(HTTPException) as exc:
        get_current_user(make_credentials("invalid.token"), db)

    assert exc.value.status_code == 401


def test_expired_token(db, data):
    token = create_token(
        {"sub": str(data["a"].id), "user_id": data["a"].id},
        expires_minutes=-1
    )

    with pytest.raises(HTTPException) as exc:
        get_current_user(make_credentials(token), db)

    assert exc.value.status_code == 401


def test_user_not_found(db):
    token = create_token({
        "sub": "2147483647",
        "user_id": 2147483647
    })

    with pytest.raises(HTTPException) as exc:
        get_current_user(make_credentials(token), db)

    assert exc.value.status_code == 401


def test_missing_user_id(db):
    token = create_token({"role": "candidate"})

    with pytest.raises(HTTPException) as exc:
        get_current_user(make_credentials(token), db)

    assert exc.value.status_code == 401


def test_get_current_user_success(db, data):
    token = make_token(data["a"])

    user = get_current_user(make_credentials(token), db)

    assert user.id == data["a"].id
    assert user.email == data["a"].email


def test_get_candidate_success(db):
    candidate = User(
        email="test_candidate_tk03@test.com",
        password_hash="x",
        role="candidate"
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    result = get_candidate(candidate)

    assert result.id == candidate.id
    assert result.role == "candidate"


def test_get_candidate_forbidden(data):
    with pytest.raises(HTTPException) as exc:
        get_candidate(data["a"])

    assert exc.value.status_code == 403


def test_get_recruiter_success(data):
    result = get_recruiter(data["a"])

    assert result.id == data["a"].id
    assert result.role == "recruiter"


def test_get_recruiter_forbidden(db):
    candidate = User(
        email="test_candidate_tk03@test.com",
        password_hash="x",
        role="candidate"
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    with pytest.raises(HTTPException) as exc:
        get_recruiter(candidate)

    assert exc.value.status_code == 403
