import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from app.models import User, Profile, ProfileSkill, CvFile, Job, JobSkill
from app.schemas.auth import RegisterIn
from app.schemas.profile import ProfileSkillIn
from app.schemas.cv import CvResult


def test_cascade_khi_xoa_user(db, data):
    ungvien = User(email="test_ungvien@test.com", password_hash="x", role="candidate")
    db.add(ungvien)
    db.commit()
    profile = Profile(user_id=ungvien.id, full_name="Ứng viên thử")
    db.add(profile)
    db.commit()
    db.add(ProfileSkill(profile_id=profile.id, skill_id=data["skill1"].id, proficiency=4, years_used=2))
    db.add(CvFile(profile_id=profile.id, file_name="a.pdf", file_path="uploads/a.pdf", file_size=100, status="pending"))
    job = Job(recruiter_id=data["a"].id, title="JD thử")
    db.add(job)
    db.commit()
    db.add(JobSkill(job_id=job.id, skill_id=data["skill1"].id, is_required=True))
    db.commit()
    profile_id, job_id = profile.id, job.id
    db.delete(ungvien)
    db.delete(data["a"])
    db.commit()
    assert db.query(Profile).filter(Profile.id == profile_id).count() == 0
    assert db.query(ProfileSkill).filter(ProfileSkill.profile_id == profile_id).count() == 0
    assert db.query(CvFile).filter(CvFile.profile_id == profile_id).count() == 0
    assert db.query(Job).filter(Job.id == job_id).count() == 0
    assert db.query(JobSkill).filter(JobSkill.job_id == job_id).count() == 0


def test_trung_email_bi_tu_choi(db, data):
    db.add(User(email="test_a@test.com", password_hash="y", role="candidate"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_trung_profile_skill_bi_tu_choi(db, data):
    ungvien = User(email="test_ungvien@test.com", password_hash="x", role="candidate")
    db.add(ungvien)
    db.commit()
    profile = Profile(user_id=ungvien.id, full_name="An")
    db.add(profile)
    db.commit()
    db.add(ProfileSkill(profile_id=profile.id, skill_id=data["skill1"].id, proficiency=4))
    db.commit()
    db.add(ProfileSkill(profile_id=profile.id, skill_id=data["skill1"].id, proficiency=3))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_khong_xoa_duoc_ky_nang_dang_dung(db, data):
    job = Job(recruiter_id=data["a"].id, title="JD thử")
    db.add(job)
    db.commit()
    db.add(JobSkill(job_id=job.id, skill_id=data["skill1"].id, is_required=True))
    db.commit()
    db.delete(data["skill1"])
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_schema_du_lieu_sai():
    with pytest.raises(ValidationError):
        RegisterIn(email="a@b.com", password="1234567", full_name="An", role="candidate")
    with pytest.raises(ValidationError):
        RegisterIn(email="a@b.com", password="12345678", full_name="An", role="admin")
    with pytest.raises(ValidationError):
        ProfileSkillIn(skill_id=1, proficiency=7, years_used=1)
    with pytest.raises(ValidationError):
        ProfileSkillIn(skill_id=1, proficiency=3, years_used=-1)
    with pytest.raises(ValidationError):
        CvResult(skills=[{"name": "Python", "proficiency": 0, "years": 1}])


def test_schema_du_lieu_dung():
    RegisterIn(email="a@b.com", password="12345678", full_name="An", role="recruiter")
    ProfileSkillIn(skill_id=1, proficiency=5, years_used=0)
