from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.schemas.evaluation import EvaluationOut
from app.services.ai_client import make_summary


def calculate_skill_score(proficiency: int, years_used: float) -> float:
    """Calculate a skill score on a 100-point scale."""
    score = (proficiency * 12) + (min(max(years_used or 0, 0), 5) * 8)
    return round(min(score, 100), 2)


def determine_level(years_experience: float, total_score: float) -> str:
    """Determine candidate level using the thresholds in the system design."""
    years = max(years_experience or 0, 0)
    if years >= 5 and total_score >= 75:
        return "Senior"
    if years >= 2 and total_score >= 55:
        return "Middle"
    if years >= 1 and total_score >= 40:
        return "Junior"
    return "Intern"


def evaluate_profile(profile: Profile) -> EvaluationOut:
    """Calculate group scores, total score, level, and AI summary for a profile."""
    grouped_scores: dict[str, list[float]] = defaultdict(list)
    summary_skills = []

    for profile_skill in profile.skills:
        skill = profile_skill.skill
        if skill is None:
            continue

        proficiency = int(profile_skill.proficiency or 1)
        years_used = float(profile_skill.years_used or 0)
        score = calculate_skill_score(proficiency, years_used)
        group_name = skill.skill_group or "Khác"
        grouped_scores[group_name].append(score)
        summary_skills.append({
            "name": skill.name,
            "proficiency": proficiency,
            "years": years_used,
        })

    groups = {
        group: round(sum(scores) / len(scores), 2)
        for group, scores in grouped_scores.items()
        if scores
    }
    total_score = round(sum(groups.values()) / len(groups), 2) if groups else 0.0
    level = determine_level(float(profile.years_experience or 0), total_score)
    summary = make_summary(
        skills=summary_skills,
        score=total_score,
        level=level,
    )

    profile.total_score = total_score
    profile.level = level
    profile.ai_summary = summary or None

    return EvaluationOut(
        total_score=total_score,
        level=level,
        groups=groups,
        summary=summary or None,
    )


def recalculate_profile_evaluation(db: Session, profile: Profile) -> EvaluationOut:
    result = evaluate_profile(profile)
    db.commit()
    db.refresh(profile)
    return result
