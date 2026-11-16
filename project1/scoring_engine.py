
import re


# ==========================================
# SCORING WEIGHTS
# ==========================================

SKILLS_WEIGHT = 35
EXPERIENCE_WEIGHT = 25
EDUCATION_WEIGHT = 15
PROJECTS_WEIGHT = 15
KEYWORDS_WEIGHT = 10

TOTAL_WEIGHT = 100


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def normalize_items(items):

    if not isinstance(items, (list, tuple, set)):
        return set()

    return {
        item.strip().casefold()
        for item in items
        if isinstance(item, str) and item.strip()
    }


def normalize_text(text):

    if not isinstance(text, str):
        return ""

    return re.sub(
        r"\s+",
        " ",
        text.strip().casefold()
    )


# ==========================================
# 1. SKILLS MATCH SCORE (35 POINTS)
# ==========================================

def calculate_skills_score(resume_skills, job_skills):

    resume_skills = normalize_items(resume_skills)
    job_skills = normalize_items(job_skills)

    if not job_skills:

        return {
            "match_percentage": None,
            "weighted_score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "status": "not_assessed"
        }

    matched_skills = resume_skills.intersection(job_skills)

    missing_skills = job_skills - resume_skills

    match_percentage = (
        len(matched_skills) / len(job_skills)
    ) * 100

    weighted_score = (
        match_percentage / 100
    ) * SKILLS_WEIGHT

    return {

        "match_percentage": round(match_percentage, 2),

        "weighted_score": round(weighted_score, 2),

        "matched_skills": sorted(matched_skills),

        "missing_skills": sorted(missing_skills),

        "status": "assessed"

    }


# ==========================================
# 2. EXPERIENCE MATCH SCORE (25 POINTS)
# ==========================================

def calculate_experience_score(resume_experience, job_experience):

    if job_experience is None:

        return {
            "match_percentage": None,
            "weighted_score": 0.0,
            "status": "not_assessed"
        }

    try:

        resume_experience = float(resume_experience)
        job_experience = float(job_experience)

        if resume_experience < 0 or job_experience < 0:
            raise ValueError("Experience cannot be negative.")

    except (TypeError, ValueError):

        return {
            "match_percentage": None,
            "weighted_score": 0.0,
            "status": "invalid_input"
        }

    if job_experience == 0:

        match_percentage = 100.0

    else:

        match_percentage = min(
            (resume_experience / job_experience) * 100,
            100.0
        )

    weighted_score = (
        match_percentage / 100
    ) * EXPERIENCE_WEIGHT

    return {

        "match_percentage": round(match_percentage, 2),

        "weighted_score": round(weighted_score, 2),

        "status": "assessed"

    }


# ==========================================
# 3. EDUCATION MATCH SCORE (15 POINTS)
# ==========================================

def calculate_education_score(resume_education, job_education):

    education_levels = {

        "none": 0,
        "high school": 1,
        "diploma": 2,
        "bachelor's": 3,
        "master's": 4,
        "phd": 5

    }

    resume_education = normalize_text(resume_education)
    job_education = normalize_text(job_education)

    if (
        resume_education not in education_levels
        or job_education not in education_levels
        or job_education == "none"
    ):

        return {

            "match_percentage": None,

            "weighted_score": 0.0,

            "status": "not_assessed"

        }

    resume_level = education_levels[resume_education]
    job_level = education_levels[job_education]

    if resume_level == 0:

        match_percentage = 0.0

    elif resume_level >= job_level:

        match_percentage = 100.0

    elif resume_level == job_level - 1:

        match_percentage = 70.0

    else:

        match_percentage = 30.0

    weighted_score = (
        match_percentage / 100
    ) * EDUCATION_WEIGHT

    return {

        "match_percentage": round(match_percentage, 2),

        "weighted_score": round(weighted_score, 2),

        "status": "assessed"

    }


# ==========================================
# 4. PROJECTS & ACHIEVEMENTS (15 POINTS)
# ==========================================

def calculate_projects_score(resume_projects, resume_certificates):

    resume_projects = (
        resume_projects
        if isinstance(resume_projects, list)
        else []
    )

    resume_certificates = (
        resume_certificates
        if isinstance(resume_certificates, list)
        else []
    )

    project_count = len([
        p for p in resume_projects
        if isinstance(p, str) and p.strip()
    ])

    certificate_count = len([
        c for c in resume_certificates
        if isinstance(c, str) and c.strip()
    ])

    # Projects: maximum 10 points
    project_score = min(
        project_count / 3,
        1.0
    ) * 10

    # Certifications: maximum 5 points
    certificate_score = min(
        certificate_count / 2,
        1.0
    ) * 5

    total_score = project_score + certificate_score

    match_percentage = (
        total_score / PROJECTS_WEIGHT
    ) * 100

    return {

        "match_percentage": round(match_percentage, 2),

        "project_score": round(project_score, 2),

        "certificate_score": round(certificate_score, 2),

        "weighted_score": round(total_score, 2),

        "status": "assessed"

    }


# ==========================================
# 5. KEYWORDS & RESPONSIBILITIES (10 POINTS)
# ==========================================

def calculate_keywords_score(resume_keywords, job_keywords):

    resume_keywords = normalize_items(resume_keywords)
    job_keywords = normalize_items(job_keywords)

    if not job_keywords:

        return {

            "match_percentage": None,

            "matched_keywords": [],

            "missing_keywords": [],

            "weighted_score": 0.0,

            "status": "not_assessed"

        }

    matched_keywords = resume_keywords.intersection(job_keywords)

    missing_keywords = job_keywords - resume_keywords

    match_percentage = (
        len(matched_keywords) / len(job_keywords)
    ) * 100

    weighted_score = (
        match_percentage / 100
    ) * KEYWORDS_WEIGHT

    return {

        "match_percentage": round(match_percentage, 2),

        "matched_keywords": sorted(matched_keywords),

        "missing_keywords": sorted(missing_keywords),

        "weighted_score": round(weighted_score, 2),

        "status": "assessed"

    }


# ==========================================
# 6. FINAL SCORE CALCULATION
# ==========================================

def calculate_final_score(
    resume_skills,
    job_skills,
    resume_experience,
    job_experience,
    resume_education,
    job_education,
    resume_projects,
    resume_certificates,
    resume_keywords,
    job_keywords
):

    # STEP 1: Calculate individual scores

    skill_score = calculate_skills_score(
        resume_skills,
        job_skills
    )

    experience_score = calculate_experience_score(
        resume_experience,
        job_experience
    )

    education_score = calculate_education_score(
        resume_education,
        job_education
    )

    project_score = calculate_projects_score(
        resume_projects,
        resume_certificates
    )

    keyword_score = calculate_keywords_score(
        resume_keywords,
        job_keywords
    )

    # STEP 2: Collect scoring results

    categories = {

        "skills": (skill_score, SKILLS_WEIGHT),

        "experience": (experience_score, EXPERIENCE_WEIGHT),

        "education": (education_score, EDUCATION_WEIGHT),

        "projects": (project_score, PROJECTS_WEIGHT),

        "keywords": (keyword_score, KEYWORDS_WEIGHT)

    }

    # STEP 3: Identify assessed categories

    assessed_weight = sum(

        weight
        for result, weight in categories.values()
        if result["status"] == "assessed"

    )

    # STEP 4: Calculate final score

    if assessed_weight == 0:

        final_score = 0.0

    else:

        earned_points = sum(

            result["weighted_score"]
            for result, weight in categories.values()
            if result["status"] == "assessed"

        )

        final_score = (
            earned_points / assessed_weight
        ) * TOTAL_WEIGHT

    # STEP 5: Return results

    return {

        "final_score": round(final_score, 2),

        "maximum_score": TOTAL_WEIGHT,

        "assessed_weight": assessed_weight,

        "assessment_coverage": round(
            (assessed_weight / TOTAL_WEIGHT) * 100,
            2
        ),

        "skills_score": skill_score["weighted_score"],

        "experience_score": experience_score["weighted_score"],

        "education_score": education_score["weighted_score"],

        "projects_score": project_score["weighted_score"],

        "keywords_score": keyword_score["weighted_score"],

        "category_details": {

            "skills": skill_score,

            "experience": experience_score,

            "education": education_score,

            "projects": project_score,

            "keywords": keyword_score

        }

    }
