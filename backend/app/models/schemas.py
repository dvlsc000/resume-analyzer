from pydantic import BaseModel, Field
from typing import List


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