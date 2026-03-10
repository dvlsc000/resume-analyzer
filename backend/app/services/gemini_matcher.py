import os
import json
from typing import Any, Dict
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Please add it to your backend/.env file."
        )
    return genai.Client(api_key=api_key)


def evaluate_with_gemini(resume_text: str, job_description: str) -> Dict[str, Any]:
    client = get_gemini_client()

    prompt = f"""
You are a strict ATS-style resume evaluator.

Your task:
Evaluate how well the RESUME matches the JOB DESCRIPTION.

Scoring rubric (0 to 100):
- 0-20: poor match
- 21-40: weak match
- 41-60: moderate match
- 61-80: strong match
- 81-100: excellent match

Rules:
1. Be strict.
2. Focus on real alignment, not generic positivity.
3. Penalize missing core requirements.
4. Reward directly relevant skills, technologies, years of experience, responsibilities, domain relevance, and achievements.
5. Do not invent information.
6. Return valid JSON only.

Return JSON with this exact structure:
{{
  "score": integer,
  "verdict": "poor match | weak match | moderate match | strong match | excellent match",
  "strengths": ["..."],
  "missing_requirements": ["..."],
  "recommendations": ["..."]
}}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}
""".strip()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "score": {"type": "integer"},
                    "verdict": {"type": "string"},
                    "strengths": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "missing_requirements": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": [
                    "score",
                    "verdict",
                    "strengths",
                    "missing_requirements",
                    "recommendations"
                ]
            }
        )
    )

    data = json.loads(response.text)

    data["score"] = max(0, min(100, int(data.get("score", 0))))
    data["strengths"] = data.get("strengths", [])[:8]
    data["missing_requirements"] = data.get("missing_requirements", [])[:8]
    data["recommendations"] = data.get("recommendations", [])[:8]
    data["verdict"] = str(data.get("verdict", "moderate match"))

    return data