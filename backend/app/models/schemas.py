from pydantic import BaseModel, Field
from typing import Dict, List


class ATSAnalysis(BaseModel):
    ats_score: float = Field(..., ge=0, le=100)
    ats_verdict: str
    detected_sections: List[str]
    contact_checks: Dict[str, bool]
    format_warnings: List[str]
    ats_improvements: List[str]


class MatchResponse(BaseModel):
    success: bool = True
    file_name: str
    embedding_score: float = Field(..., ge=0, le=100)
    gemini_score: float = Field(..., ge=0, le=100)
    final_score: float = Field(..., ge=0, le=100)
    verdict: str
    strengths: List[str]
    missing_requirements: List[str]
    recommendations: List[str]
    resume_preview: str
    ats_analysis: ATSAnalysis