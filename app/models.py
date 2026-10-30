from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, model_validator

class PetitionCategory(str, Enum):
    attendance = "attendance"
    re_evaluation = "re_evaluation"
    re_registration = "re_registration"
    medical_leave = "medical_leave"
    grade_grievance = "grade_grievance"

class PetitionRequest(BaseModel):
    category: PetitionCategory
    description: str = Field(min_length=10, max_length=4000)
    attendance_percentage: float | None = Field(default=None, ge=0, le=100)
    prescribed_minimum: float | None = Field(default=None, ge=0, le=100)
    medical_documented: bool = False
    condonation_requested: bool = False
    student_reference: str | None = Field(default=None, min_length=1, max_length=80)

    @model_validator(mode="after")
    def cross_fields(self):
        if self.category == PetitionCategory.attendance:
            if self.attendance_percentage is None or self.prescribed_minimum is None:
                raise ValueError("attendance petitions require attendance_percentage and prescribed_minimum")
        if self.condonation_requested and not self.medical_documented and self.category == PetitionCategory.attendance:
            raise ValueError("medical_documented must be true when medical condonation is requested")
        return self

class Citation(BaseModel):
    source_id: str
    document: str
    page: int
    clause: str
    passage: str

class TriageResult(BaseModel):
    advisory_notice: str = "Advisory eligibility assessment; an authorised examination officer makes the final decision."
    petition_facts: dict[str, Any]
    base_provision: Citation | None = None
    modifying_provision: Citation | None = None
    missing_information: list[str] = []
    conflicts: list[str] = []
    proposed_eligibility: str
    routing: str
    human_review_required: bool
    verification: str
    citations: list[Citation]
    prompt_version: str = "petition-analyst-v1/research-verifier-v1"

class FeedbackRequest(BaseModel):
    run_id: str = Field(min_length=1, max_length=80)
    category: str = Field(min_length=1, max_length=40)
    useful: bool
    citations_correct: bool
    comments: str | None = Field(default=None, max_length=1000)

