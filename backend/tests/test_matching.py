from app.models import Profile, ProfileSkill, Job, JobSkill, Skill
from app.services.matching_service import calc_match

PYTHON = Skill(id=1, name="Python", skill_group="Backend")
FASTAPI = Skill(id=2, name="FastAPI", skill_group="Backend")
SQL = Skill(id=3, name="SQL", skill_group="Database")
DOCKER = Skill(id=4, name="Docker", skill_group="DevOps")
GIT = Skill(id=5, name="Git", skill_group="DevOps")


def make_job(min_years, required, preferred):
    job = Job(min_years=min_years)
    for skill in required:
        job.skills.append(JobSkill(skill_id=skill.id, skill=skill, is_required=True))
    for skill in preferred:
        job.skills.append(JobSkill(skill_id=skill.id, skill=skill, is_required=False))
    return job


def make_profile(years, levels):
    profile = Profile(years_experience=years)
    for skill_id, proficiency in levels.items():
        profile.skills.append(ProfileSkill(skill_id=skill_id, proficiency=proficiency))
    return profile


def backend_job():
    return make_job(2, [PYTHON, FASTAPI, SQL], [DOCKER, GIT])


def test_vi_du_1_khop_du_het():
    profile = make_profile(3, {1: 4, 2: 3, 3: 5, 4: 3, 5: 4})
    percent, matched, missing = calc_match(profile, backend_job())
    assert percent == 100.0
    assert matched == ["FastAPI", "Python", "SQL", "Docker", "Git"]
    assert missing == []


def test_vi_du_2_thieu_mot_bat_buoc_va_mot_uu_tien():
    profile = make_profile(1, {1: 4, 2: 2, 3: 3, 4: 3, 5: 1})
    percent, matched, missing = calc_match(profile, backend_job())
    assert percent == 60.0
    assert matched == ["Python", "SQL", "Docker"]
    assert missing == ["FastAPI", "Git"]


def test_vi_du_3_proficiency_dung_nguong_3_la_khop_2_la_thieu():
    profile = make_profile(1, {1: 3, 2: 3, 3: 2})
    percent, matched, missing = calc_match(profile, backend_job())
    assert percent == 50.0
    assert matched == ["FastAPI", "Python"]
    assert missing == ["SQL", "Docker", "Git"]


def test_vi_du_4_ho_so_khong_co_ky_nang():
    percent, matched, missing = calc_match(make_profile(0, {}), backend_job())
    assert percent == 0.0
    assert matched == []
    assert missing == ["FastAPI", "Python", "SQL", "Docker", "Git"]


def test_vi_du_5_jd_khong_co_ky_nang_bat_buoc_thi_du_60_diem():
    job = make_job(4, [], [DOCKER, GIT])
    percent, matched, missing = calc_match(make_profile(1, {4: 5}), job)
    assert percent == 75.0
    assert matched == ["Docker"]
    assert missing == ["Git"]


def test_vi_du_6_jd_khong_ky_nang_va_min_years_0_thi_du_100():
    percent, matched, missing = calc_match(make_profile(0, {}), make_job(0, [], []))
    assert percent == 100.0
    assert matched == []
    assert missing == []


def test_so_nam_vuot_yeu_cau_chi_tinh_toi_da_20_diem():
    job = make_job(2, [PYTHON], [])
    percent, _, _ = calc_match(make_profile(10, {1: 5}), job)
    assert percent == 100.0


def test_lam_tron_mot_chu_so_thap_phan():
    job = make_job(0, [PYTHON, FASTAPI, SQL], [DOCKER, GIT, Skill(id=6, name="AWS", skill_group="DevOps")])
    percent, _, _ = calc_match(make_profile(0, {1: 4, 2: 4, 4: 4}), job)
    assert percent == 66.7


def test_years_experience_none_tinh_la_0():
    job = make_job(2, [PYTHON], [])
    percent, _, _ = calc_match(make_profile(None, {1: 5}), job)
    assert percent == 80.0