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