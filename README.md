# Resume Analyzer

Most resume tools either overpromise or oversimplify.

This one tries to do neither.

It gives you a realistic picture of how your resume performs — not just structurally (ATS), but also in terms of how well it actually matches a job.

---

## What this does

Upload a resume and a job description.

The system evaluates both and answers one question:

> **“How well does this resume actually match this job?”**

Instead of a single vague score, you get a breakdown:

- ATS readability (format, structure, parsing issues)
- semantic similarity (does your experience align?)
- keyword coverage (are you hitting what matters?)
- AI evaluation (what a strict reviewer would say)

---

## Why this exists

Most people tweak resumes blindly.

- Add more buzzwords  
- Reorder sections  
- Copy templates  

Still no callbacks.

The problem isn’t effort — it’s feedback.

This project is built to make that feedback immediate, structured, and actually useful.

---

## How it works

### 1. Text extraction

Supports:
- PDF  
- DOCX  
- DOC  

All files are converted into clean, normalized text before analysis.

---

### 2. ATS analysis

The resume is evaluated like an ATS system:

- detects sections (skills, experience, education, etc.)
- checks for contact details (email, phone, links, location)
- flags formatting issues (symbols, long lines, tabs)
- validates consistency (e.g. date formats)

Outputs:
- ATS score
- verdict (ATS-friendly → high risk)
- warnings
- improvement suggestions

---

### 3. Embedding-based matching

Uses sentence embeddings to measure real alignment:

- full document similarity
- chunk-level comparison (captures coverage of requirements)
- keyword overlap scoring

These are combined into a calibrated 0–100 score.

---

### 4. LLM evaluation (Gemini)

Adds a stricter, human-style review layer:

- identifies strengths
- highlights missing requirements
- provides actionable recommendations
- assigns a structured score and verdict

No fluff — just structured output.

---

### 5. Final scoring

A hybrid score combines both approaches:

- 40% embedding score  
- 60% LLM score  

This balances objective similarity with real-world relevance.

---

## Output

You don’t just get a number.

You get a full breakdown:

- match score (0–100)
- verdict (poor → excellent)
- strengths
- missing requirements
- recommendations
- ATS analysis (score + issues + improvements)

---

## What makes this different

Most resume tools do one thing:

- keyword matching  
- basic ATS checks  
- generic AI feedback  

This combines all three — and connects them.

It doesn’t just say *“your resume is good”*  
It shows **why it works or doesn’t**.

---

## Tech stack

- Python (backend logic)
- Sentence Transformers (semantic similarity)
- Google Gemini API (LLM evaluation)
- Pydantic (structured responses)
- PDF / DOCX parsing tools
- React (frontend)

---

## Running locally

```bash
# clone repo
git clone https://github.com/dvlsc000/resume-analyzer.git

# enter project
cd resume-analyzer

# install dependencies
pip install -r requirements.txt

# add your API key in .env
GEMINI_API_KEY=your_key_here

# run the app
python app.py
