
from pydantic import BaseModel, Field


class JobSchema(BaseModel):

    job_title: str | None = None
    company_name: str | None = None

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)

    required_experience_years: float | None = None

    required_education: list[str] = Field(default_factory=list)

    responsibilities: list[str] = Field(default_factory=list)

    required_certifications: list[str] = Field(default_factory=list)
    preferred_certifications: list[str] = Field(default_factory=list)
