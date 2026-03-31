'''
models/schemas.py: definations of llm output structures
'''
from pydantic import BaseModel, Field

class JDInfo(BaseModel):
    """Structured information extracted from a job description."""
    title: str = Field(description="The title of the job")
    required_skills: list[str] = Field(description="List of all required skills for this job")
    preferred_skills: list[str] = Field(description="List of all preferred or nice-to-have skills")
    responsibilities: list[str] = Field(description="List of main responsibilities for this job")
    education_requirments: str = Field(description="The requirment of education background")

class CVInfo(BaseModel):
    """Structured information extracted from a CV."""
    name: str = Field(description="The name of this candidate")
    education: list[str] = Field(description="List of all education experience of this candidate")
    skills: list[str] = Field(description="List of all skills this candidate have")
    projects: list[str] = Field(description="List of all projects done by this candidate")
    experience: list[str] = Field(description="List of all experience this condidate have except their projects")
    highlights: list[str] = Field(description="List of highlights of this candidate summarized from provided cv")
    target_roles: list[str] = Field(description="List of possible roles suitable for this candidate")

class MatchResult(BaseModel):
    """Structured information of matching result for uploaded cv and jd."""
    match_score: float = Field(description="A score of the matching result")
    missing_skills: list[str] = Field(description="List of all skills mising from the provided job description")
    strengths: list[str] = Field(description="List of all strengths the candidate have for applying provided job")
    suggestion: str = Field(description="A short suggestion for this candidate")