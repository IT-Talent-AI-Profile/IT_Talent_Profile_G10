import pytest
from app.db.session import SessionLocal
from app.models import User, Skill


def don_dep(db):
    db.rollback()
    db.query(User).filter(User.email.like("test\\_%@test.com")).delete(synchronize_session=False)
    db.query(Skill).filter(Skill.name.like("Skill\\_test\\_%")).delete(synchronize_session=False)
    db.commit()


@pytest.fixture
def db():
    session = SessionLocal()
    don_dep(session)
    yield session
    don_dep(session)
    session.close()


@pytest.fixture
def data(db):
    skill1 = Skill(name="Skill_test_1", skill_group="Khác")
    skill2 = Skill(name="Skill_test_2", skill_group="Khác")
    ntd_a = User(email="test_a@test.com", password_hash="x", role="recruiter")
    ntd_b = User(email="test_b@test.com", password_hash="x", role="recruiter")
    db.add_all([skill1, skill2, ntd_a, ntd_b])
    db.commit()
    return {"skill1": skill1, "skill2": skill2, "a": ntd_a, "b": ntd_b}
