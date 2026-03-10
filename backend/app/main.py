import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import MatchResponse
from app.services.text_extractor import extract_resume_text, normalize_text
from app.services.embedding_matcher import score_resume_vs_job
from app.services.gemini_matcher import evaluate_with_gemini
from app.services.scoring import combine_scores, get_verdict_from_score


app = FastAPI(title="Resume Matcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE_MB = 10


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/upload", response_model=MatchResponse)
async def upload_resume(
    resume: UploadFile = File(...),
    jobDescription: str = Form(...)
):
    try:
        if not resume.filename:
            raise HTTPException(status_code=400, detail="Missing file name.")

        ext = Path(resume.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        if not jobDescription.strip():
            raise HTTPException(status_code=400, detail="Job description is required.")

        file_bytes = await resume.read()

        file_size_mb = len(file_bytes) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(status_code=400, detail="File too large. Max 10 MB.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(file_bytes)
            temp_path = tmp.name

        try:
            resume_text = extract_resume_text(temp_path)
            resume_text = normalize_text(resume_text)
            job_description = normalize_text(jobDescription)

            if not resume_text:
                raise HTTPException(status_code=400, detail="Could not extract text from resume.")

            resume_for_scoring = resume_text[:15000]
            jd_for_scoring = job_description[:12000]

            embedding_score = score_resume_vs_job(resume_for_scoring, jd_for_scoring)

            gemini_result = evaluate_with_gemini(
                resume_text=resume_for_scoring,
                job_description=jd_for_scoring,
            )
            gemini_score = float(gemini_result["score"])

            final_score = combine_scores(
                embedding_score=embedding_score,
                gemini_score=gemini_score
            )

            verdict = get_verdict_from_score(final_score)

            return MatchResponse(
                file_name=resume.filename,
                embedding_score=embedding_score,
                gemini_score=gemini_score,
                final_score=final_score,
                verdict=verdict,
                strengths=gemini_result.get("strengths", []),
                missing_requirements=gemini_result.get("missing_requirements", []),
                recommendations=gemini_result.get("recommendations", []),
                resume_preview=resume_text[:500]
            )

        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")