
from pydantic import BaseModel, Field
from typing import Optional


class UserInput(BaseModel):

    # Personal Information
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None

    # Resume Information
    skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)

    languages: Optional[list[str]] = None
    hobbies: Optional[list[str]] = None
