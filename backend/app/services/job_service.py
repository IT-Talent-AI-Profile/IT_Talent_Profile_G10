from fastapi import HTTPException
from app.models import Job, JobSkill, Skill


def job_to_dict(job):
    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "min_years": job.min_years,
        "is_open": job.is_open,
        "skills": [
            {"skill_id": item.skill_id, "name": item.skill.name, "is_required": item.is_required}
            for item in job.skills
        ],
    }


def find_job(db, recruiter_id, job_id):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy JD")
    return job


def create_job(db, recruiter_id, data):
    job = Job(recruiter_id=recruiter_id, title=data.title, description=data.description, min_years=data.min_years)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job_to_dict(job)


def list_jobs(db, recruiter_id):
    jobs = db.query(Job).filter(Job.recruiter_id == recruiter_id).order_by(Job.created_at.desc(), Job.id.desc()).all()
    return [job_to_dict(job) for job in jobs]


def get_job(db, recruiter_id, job_id):
    return job_to_dict(find_job(db, recruiter_id, job_id))


def update_job(db, recruiter_id, job_id, data):
    job = find_job(db, recruiter_id, job_id)
    job.title = data.title
    job.description = data.description
    job.min_years = data.min_years
    db.commit()
    db.refresh(job)
    return job_to_dict(job)


def delete_job(db, recruiter_id, job_id):
    job = find_job(db, recruiter_id, job_id)
    db.delete(job)
    db.commit()


def set_status(db, recruiter_id, job_id, is_open):
    job = find_job(db, recruiter_id, job_id)
    job.is_open = is_open
    db.commit()
    db.refresh(job)
    return job_to_dict(job)


def add_skill(db, recruiter_id, job_id, data):
    job = find_job(db, recruiter_id, job_id)
    skill = db.query(Skill).filter(Skill.id == data.skill_id).first()
    if skill is None:
        raise HTTPException(status_code=404, detail="Kỹ năng không tồn tại")
    item = db.query(JobSkill).filter(JobSkill.job_id == job.id, JobSkill.skill_id == skill.id).first()
    if item is None:
        db.add(JobSkill(job_id=job.id, skill_id=skill.id, is_required=data.is_required))
    else:
        item.is_required = data.is_required
    db.commit()
    db.refresh(job)
    return job_to_dict(job)


def remove_skill(db, recruiter_id, job_id, skill_id):
    job = find_job(db, recruiter_id, job_id)
    item = db.query(JobSkill).filter(JobSkill.job_id == job.id, JobSkill.skill_id == skill_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="JD chưa có kỹ năng này")
    db.delete(item)
    db.commit()
    db.refresh(job)
    return job_to_dict(job)