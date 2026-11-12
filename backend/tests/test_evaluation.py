import pytest

from app.models.profile import Profile
from app.models.profile_skill import ProfileSkill
from app.models.skill import Skill
from app.services import evaluation_service


def make_profile(years_experience=0, skills=None):
    profile = Profile(
        user_id=1,
        full_name="Evaluation Test",
        years_experience=years_experience,
    )
    profile.skills = skills or []
    return profile


def make_profile_skill(name, group, proficiency, years_used):
    skill = Skill(name=name, skill_group=group)
    return ProfileSkill(
        skill=skill,
        proficiency=proficiency,
        years_used=years_used,
    )


@pytest.mark.parametrize(
    ("proficiency", "years_used", "expected"),
    [
        (1, 0, 12),
        (3, 1, 44),
        (4, 2.5, 68),
        (5, 10, 100),
    ],
)
def test_calculate_skill_score(proficiency, years_used, expected):
    assert evaluation_service.calculate_skill_score(proficiency, years_used) == expected


@pytest.mark.parametrize(
    ("years", "score", "expected"),
    [
        (5, 75, "Senior"),
        (2, 55, "Middle"),
        (1, 40, "Junior"),
        (4.9, 90, "Middle"),
        (0.9, 90, "Intern"),
        (8, 74.99, "Middle"),
    ],
)
def test_determine_level(years, score, expected):
    assert evaluation_service.determine_level(years, score) == expected


def test_evaluate_profile_calculates_group_and_total_scores(monkeypatch):
    monkeypatch.setattr(
        evaluation_service,
        "make_summary",
        lambda **kwargs: "Summary generated for test",
    )
    profile = make_profile(
        years_experience=2.5,
        skills=[
            make_profile_skill("Python", "Backend", 4, 2.5),
            make_profile_skill("FastAPI", "Backend", 3, 1),
            make_profile_skill("React", "Frontend", 4, 2.5),
        ],
    )

    result = evaluation_service.evaluate_profile(profile)

    # Backend: (68 + 44) / 2 = 56; Frontend: 68; total: 62.
    assert result.groups == {"Backend": 56.0, "Frontend": 68.0}
    assert result.total_score == 62.0
    assert result.level == "Middle"
    assert result.summary == "Summary generated for test"
    assert profile.total_score == 62.0
    assert profile.level == "Middle"
    assert profile.ai_summary == "Summary generated for test"


def test_evaluate_profile_without_skills_returns_intern(monkeypatch):
    monkeypatch.setattr(evaluation_service, "make_summary", lambda **kwargs: "")
    profile = make_profile(years_experience=0)

    result = evaluation_service.evaluate_profile(profile)

    assert result.groups == {}
    assert result.total_score == 0
    assert result.level == "Intern"
    assert result.summary is None
    assert profile.total_score == 0
    assert profile.level == "Intern"
    assert profile.ai_summary is None


def test_evaluate_profile_passes_confirmed_skills_to_summary(monkeypatch):
    captured = {}

    def fake_summary(**kwargs):
        captured.update(kwargs)
        return "Candidate summary"

    monkeypatch.setattr(evaluation_service, "make_summary", fake_summary)
    profile = make_profile(
        years_experience=1,
        skills=[make_profile_skill("Python", "Backend", 3, 1)],
    )

    evaluation_service.evaluate_profile(profile)

    assert captured["skills"] == [
        {"name": "Python", "proficiency": 3, "years": 1.0}
    ]
    assert captured["score"] == 44.0
    assert captured["level"] == "Junior"
