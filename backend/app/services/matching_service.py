from fastapi import HTTPException
from app.models import Profile, ProfileSkill

PAGE_SIZE = 10
MIN_PROFICIENCY = 3


def calc_match(profile, job):
    have = {item.skill_id: item.proficiency for item in profile.skills}
    matched = []
    missing = []
    required_total = 0
    required_hit = 0
    preferred_total = 0
    preferred_hit = 0
    for item in sorted(job.skills, key=lambda x: (not x.is_required, x.skill.name)):
        hit = have.get(item.skill_id, 0) >= MIN_PROFICIENCY
        if hit:
            matched.append(item.skill.name)
        else:
            missing.append(item.skill.name)
        if item.is_required:
            required_total += 1
            required_hit += int(hit)
        else:
            preferred_total += 1
            preferred_hit += int(hit)
    required_score = 60 if required_total == 0 else 60 * required_hit / required_total
    preferred_score = 20 if preferred_total == 0 else 20 * preferred_hit / preferred_total
    min_years = job.min_years or 0
    years = profile.years_experience or 0
    years_score = 20 if min_years == 0 else 20 * min(years / min_years, 1)
    percent = round(required_score + preferred_score + years_score, 1)
    return percent, matched, missing


def parse_skill_ids(text):
    ids = []
    for part in text.split(","):
        part = part.strip()
        if part == "":
            continue
        if not part.isdigit():
            raise HTTPException(status_code=422, detail="skill_ids phải là các số cách nhau bằng dấu phẩy, ví dụ 1,2")
        ids.append(int(part))
    return ids


def candidate_to_item(profile):
    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "desired_position": profile.desired_position,
        "years_experience": profile.years_experience or 0,
        "level": profile.level,
        "total_score": profile.total_score,
    }


def search_candidates(db, skill_ids_text, level, page):
    query = db.query(Profile).filter(Profile.is_public == True)
    for skill_id in set(parse_skill_ids(skill_ids_text)):
        query = query.filter(Profile.skills.any(ProfileSkill.skill_id == skill_id))
    if level != "":
        query = query.filter(Profile.level == level)
    total = query.count()
    profiles = query.order_by(Profile.total_score.desc(), Profile.id).offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE).all()
    return {
        "total": total,
        "page": page,
        "page_size": PAGE_SIZE,
        "items": [candidate_to_item(profile) for profile in profiles],
    }


def get_candidate_detail(db, profile_id):
    profile = db.query(Profile).filter(Profile.id == profile_id, Profile.is_public == True).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ ứng viên")
    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "desired_position": profile.desired_position,
        "years_experience": profile.years_experience or 0,
        "education": profile.education,
        "experience": profile.experience,
        "github_url": profile.github_url,
        "is_public": profile.is_public,
        "level": profile.level,
        "total_score": profile.total_score,
        "ai_summary": profile.ai_summary,
        "skills": [
            {
                "skill_id": item.skill_id,
                "name": item.skill.name,
                "group": item.skill.skill_group,
                "proficiency": item.proficiency,
                "years_used": item.years_used or 0,
            }
            for item in profile.skills
        ],
    }


def get_job_matches(db, current_user, job_id, page=1):
    from app.models.job import Job

    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None or job.recruiter_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tin tuyển dụng không tồn tại")

    if not job.is_open:
        raise HTTPException(status_code=400, detail="Tin tuyển dụng đã đóng")

    if page < 1:
        raise HTTPException(status_code=422, detail="page phải từ 1 trở lên")

    profiles = db.query(Profile).filter(Profile.is_public == True).all()

    match_items = []
    for profile in profiles:
        percent, matched, missing = calc_match(profile, job)
        match_items.append({
            "id": profile.id,
            "full_name": profile.full_name,
            "desired_position": profile.desired_position,
            "years_experience": profile.years_experience or 0,
            "level": profile.level,
            "total_score": profile.total_score,
            "match_percent": percent,
            "matched_skills": matched,
            "missing_skills": missing,
        })

    match_items.sort(key=lambda x: (-x["match_percent"], -(x["total_score"] or 0), x["id"]))

    total = len(match_items)
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    items = match_items[start:end]

    return {
        "job": job.title,
        "total": total,
        "page": page,
        "page_size": PAGE_SIZE,
        "items": items,
    }
