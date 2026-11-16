
import logging
import re
from io import BytesIO

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from starlette.concurrency import run_in_threadpool

from pdf_reader import extract_text_from_pdf

from llm.structured_extractor import (
    extract_resume_data,
    extract_job_data,
    generate_feedback
)

from scoring_engine import calculate_final_score


# ==========================================
# CONFIGURATION
# ==========================================

router = APIRouter()

logger = logging.getLogger(__name__)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def convert_to_dict(data):
    """Convert Pydantic models into dictionaries."""

    if hasattr(data, "model_dump"):
        return data.model_dump()

    if hasattr(data, "dict"):
        return data.dict()

    if isinstance(data, dict):
        return data

    raise TypeError(
        "Unsupported data format returned by extractor."
    )


def clean_string_list(items):
    """Keep only non-empty strings."""

    if not isinstance(items, list):
        return []

    return [
        item.strip()
        for item in items
        if isinstance(item, str) and item.strip()
    ]


def extract_experience_years(experience_list):
    """
    Extract the highest explicitly mentioned experience duration.

    Note: This does not calculate duration from employment dates.
    """

    experience_list = clean_string_list(experience_list)

    years = []

    for experience in experience_list:

        matches = re.findall(
            r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
            experience,
            re.IGNORECASE
        )

        years.extend(
            float(match)
            for match in matches
        )

    return max(years, default=0.0)


def normalize_education(education_list):
    """Return the highest recognized education level."""

    education_list = clean_string_list(education_list)

    education_levels = {
        "high school": 1,
        "diploma": 2,
        "bachelor's": 3,
        "master's": 4,
        "phd": 5
    }

    detected_levels = []

    for education in education_list:

        education = education.casefold()

        if "phd" in education or "doctorate" in education:
            detected_levels.append("phd")

        elif (
            "master" in education
            or "mba" in education
            or re.search(r"\bms\b", education)
        ):
            detected_levels.append("master's")

        elif (
            "bachelor" in education
            or re.search(r"\bbsc\b", education)
            or re.search(r"\bbs\b", education)
            or "b.tech" in education
        ):
            detected_levels.append("bachelor's")

        elif "diploma" in education:
            detected_levels.append("diploma")

        elif (
            "high school" in education
            or "intermediate" in education
        ):
            detected_levels.append("high school")

    if not detected_levels:
        return "none"

    return max(
        detected_levels,
        key=lambda level: education_levels[level]
    )


def validate_job_extraction(job):
    """Ensure meaningful job requirements were extracted."""

    requirement_fields = [
        "required_skills",
        "preferred_skills",
        "required_education",
        "responsibilities",
        "required_certifications",
        "preferred_certifications"
    ]

    has_requirements = any(
        clean_string_list(job.get(field, []))
        for field in requirement_fields
    )

    has_experience_requirement = (
        job.get("required_experience_years") is not None
    )

    if not has_requirements and not has_experience_requirement:

        raise HTTPException(
            status_code=422,
            detail=(
                "Could not extract meaningful requirements "
                "from the job description."
            )
        )


def normalize_skill(skill):
    """Normalize skill names."""

    return skill.strip().casefold()


# ==========================================
# ANALYZE RESUME ENDPOINT
# ==========================================

@router.post("/analyze")
async def analyze_resume(

    resume_file: UploadFile = File(...),

    job_description: str = Form(...)

):

    # ======================================
    # STEP 1: VALIDATE INPUT
    # ======================================

    if (
        not resume_file.filename
        or not resume_file.filename.lower().endswith(".pdf")
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    if not job_description or not job_description.strip():

        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    try:

        # ==================================
        # STEP 2: READ PDF
        # ==================================

        pdf_content = await resume_file.read()

        if not pdf_content:

            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )

        if b"%PDF" not in pdf_content[:1024]:

            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file."
            )

        # ==================================
        # STEP 3: EXTRACT PDF TEXT
        # ==================================

        extracted_text = await run_in_threadpool(
            extract_text_from_pdf,
            BytesIO(pdf_content)
        )

        if not extracted_text or not extracted_text.strip():

            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text found in the PDF. "
                    "The document may be scanned or image-based."
                )
            )

        # ==================================
        # STEP 4: EXTRACT RESUME INFORMATION
        # ==================================

        resume_data = await run_in_threadpool(
            extract_resume_data,
            extracted_text
        )

        # ==================================
        # STEP 5: EXTRACT JOB INFORMATION
        # ==================================

        job_data = await run_in_threadpool(
            extract_job_data,
            job_description.strip()
        )

        # ==================================
        # STEP 6: CONVERT TO DICTIONARIES
        # ==================================

        resume = convert_to_dict(resume_data)

        job = convert_to_dict(job_data)

        validate_job_extraction(job)

        # ==================================
        # STEP 7: PREPARE SCORING INPUTS
        # ==================================

        resume_skills = clean_string_list(
            resume.get("skills", [])
        )

        required_skills = clean_string_list(
            job.get("required_skills", [])
        )

        preferred_skills = clean_string_list(
            job.get("preferred_skills", [])
        )

        job_skills = required_skills + preferred_skills

        resume_experience = extract_experience_years(
            resume.get("experience", [])
        )

        job_experience = job.get(
            "required_experience_years"
        )

        resume_education = normalize_education(
            resume.get("education", [])
        )

        job_education = normalize_education(
            job.get("required_education", [])
        )

        resume_projects = clean_string_list(
            resume.get("projects", [])
        )

        resume_certificates = clean_string_list(
            resume.get("certifications", [])
        )

        # Resume keywords
        resume_keywords = (
            resume_skills
            + clean_string_list(resume.get("experience", []))
            + resume_projects
            + resume_certificates
        )

        # Job keywords
        job_keywords = (
            job_skills
            + clean_string_list(job.get("responsibilities", []))
            + clean_string_list(
                job.get("required_certifications", [])
            )
            + clean_string_list(
                job.get("preferred_certifications", [])
            )
        )

        # ==================================
        # STEP 8: DEBUG INPUTS
        # ==================================

        logger.info("========== SCORING INPUTS ==========")

        logger.info("Resume skills: %s", resume_skills)

        logger.info("Job skills: %s", job_skills)

        logger.info("Resume experience: %s", resume_experience)

        logger.info("Job experience: %s", job_experience)

        logger.info("Resume education: %s", resume_education)

        logger.info("Job education: %s", job_education)

        logger.info("Resume projects: %s", resume_projects)

        logger.info("Resume certificates: %s", resume_certificates)

        # ==================================
        # STEP 9: CALCULATE FINAL SCORE
        # ==================================

        score_result = calculate_final_score(

            resume_skills=resume_skills,

            job_skills=job_skills,

            resume_experience=resume_experience,

            job_experience=job_experience,

            resume_education=resume_education,

            job_education=job_education,

            resume_projects=resume_projects,

            resume_certificates=resume_certificates,

            resume_keywords=resume_keywords,

            job_keywords=job_keywords

        )

        # ==================================
        # STEP 10: SKILLS ANALYSIS
        # ==================================

        skill_details = score_result["category_details"]["skills"]

        matched_skills = skill_details["matched_skills"]

        missing_skills = skill_details["missing_skills"]

        # ==================================
        # STEP 11: GENERATE AI FEEDBACK
        # ==================================

        feedback = await run_in_threadpool(

            generate_feedback,

            resume,

            job,

            score_result

        )

        # ==================================
        # STEP 12: ASSESSMENT STATUS
        # ==================================

        assessment_status = {

            category: details["status"]

            for category, details
            in score_result["category_details"].items()

        }

        # ==================================
        # STEP 13: API RESPONSE
        # ==================================

        return {

            "status": "success",

            "message": "Resume analysis completed successfully!",

            "overall_score": score_result["final_score"],

            "maximum_score": score_result["maximum_score"],

            "assessment_coverage": score_result["assessment_coverage"],

            "score_breakdown": score_result["category_details"],

            "assessment_status": assessment_status,

            "skills_analysis": {

                "matched_skills": matched_skills,

                "missing_skills": missing_skills

            },

            "feedback": feedback,

            "resume_information": resume,

            "job_information": job

        }

    except HTTPException:

        raise

    except Exception as e:

        logger.exception("Resume analysis failed.")

        raise HTTPException(

            status_code=500,

            detail=(
                "An unexpected error occurred "
                "while analyzing the resume."
            )

        ) from e
