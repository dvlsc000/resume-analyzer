import re
from typing import Any, Dict, List


COMMON_SECTION_PATTERNS = {
    "contact": [r"\bcontact\b"],
    "summary": [r"\bsummary\b", r"\bprofessional summary\b", r"\bprofile\b", r"\babout me\b"],
    "skills": [r"\bskills\b", r"\btechnical skills\b", r"\bcore competencies\b", r"\btech stack\b"],
    "experience": [r"\bexperience\b", r"\bwork experience\b", r"\bprofessional experience\b", r"\bemployment\b"],
    "projects": [r"\bprojects\b", r"\bpersonal projects\b", r"\bkey projects\b"],
    "education": [r"\beducation\b", r"\bacademic background\b", r"\bqualifications\b"],
    "certifications": [r"\bcertifications\b", r"\blicenses\b"],
    "awards": [r"\bawards\b", r"\bachievements\b"],
}


def _normalize_lines(text: str) -> List[str]:
    lines = [line.strip() for line in text.splitlines()]
    return [line for line in lines if line]


def _find_sections(lines: List[str]) -> List[str]:
    found_sections = []

    for line in lines:
        lowered = line.lower()
        for section_name, patterns in COMMON_SECTION_PATTERNS.items():
            if section_name in found_sections:
                continue

            if any(re.search(pattern, lowered) for pattern in patterns):
                found_sections.append(section_name)

    return found_sections


def _detect_email(text: str) -> bool:
    return bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text))


def _detect_phone(text: str) -> bool:
    return bool(re.search(r"(\+?\d[\d\-\s\(\)]{7,}\d)", text))


def _detect_linkedin(text: str) -> bool:
    return "linkedin.com" in text.lower()


def _detect_github(text: str) -> bool:
    return "github.com" in text.lower()


def _detect_location(text: str) -> bool:
    """
    Very simple location heuristic.
    We look for 'City, ST' or 'City, Country' style patterns.
    """
    return bool(re.search(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s?[A-Z][A-Za-z]{1,}\b", text))


def _extract_dates(text: str) -> List[str]:
    patterns = [
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
        r"\b\d{1,2}/\d{4}\b",
        r"\b\d{4}\b",
        r"\b\d{1,2}-\d{4}\b",
    ]

    matches = []
    for pattern in patterns:
        matches.extend(re.findall(pattern, text, flags=re.IGNORECASE))

    return matches


def _date_format_warnings(date_strings: List[str]) -> List[str]:
    warnings = []

    has_month_year = any(re.match(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)", d, re.I) for d in date_strings)
    has_slash = any("/" in d for d in date_strings)
    has_dash = any("-" in d for d in date_strings)
    has_year_only = any(re.fullmatch(r"\d{4}", d) for d in date_strings)

    used_formats = sum([has_month_year, has_slash, has_dash, has_year_only])

    if used_formats >= 3:
        warnings.append("Multiple date styles detected. Use one consistent format across all roles.")

    return warnings


def _special_character_warnings(text: str) -> List[str]:
    warnings = []

    weird_symbols = re.findall(r"[■◆►◉★☆✓✔✦➜➤➝❖❯]+", text)
    if weird_symbols:
        warnings.append("Decorative symbols detected. Some ATS systems parse symbols poorly.")

    if "|" in text:
        warnings.append("Pipe characters (|) detected. Excessive use can reduce readability in ATS parsers.")

    return warnings


def _section_warnings(found_sections: List[str]) -> List[str]:
    warnings = []

    recommended = {"summary", "skills", "experience", "education"}
    missing_recommended = recommended - set(found_sections)

    if missing_recommended:
        warnings.append(
            "Missing or unclear standard sections: " + ", ".join(sorted(missing_recommended))
        )

    if "skills" not in found_sections:
        warnings.append("No clearly labeled Skills section detected.")
    if "experience" not in found_sections:
        warnings.append("No clearly labeled Experience section detected.")

    return warnings


def _content_warnings(lines: List[str], text: str) -> List[str]:
    warnings = []

    long_lines = [line for line in lines if len(line) > 180]
    if len(long_lines) >= 3:
        warnings.append("Several very long lines detected. Dense formatting can reduce readability.")

    uppercase_lines = [line for line in lines if line.isupper() and len(line.split()) >= 3]
    if len(uppercase_lines) >= 8:
        warnings.append("Heavy use of uppercase text detected. This can reduce scannability.")

    bullet_lines = [line for line in lines if re.match(r"^[-•*]\s+", line)]
    if len(bullet_lines) < 3:
        warnings.append("Very few bullet points detected. Bullet-based experience sections are usually easier to scan.")

    if text.count("\t") > 5:
        warnings.append("Tab-heavy formatting detected. ATS systems may parse tabs inconsistently.")

    return warnings


def _contact_warnings(text: str) -> List[str]:
    warnings = []

    if not _detect_email(text):
        warnings.append("Email address not clearly detected.")
    if not _detect_phone(text):
        warnings.append("Phone number not clearly detected.")
    if not (_detect_linkedin(text) or _detect_github(text)):
        warnings.append("No LinkedIn or GitHub/profile link detected.")
    if not _detect_location(text):
        warnings.append("Location not clearly detected.")

    return warnings


def _build_improvements(warnings: List[str], found_sections: List[str]) -> List[str]:
    suggestions = []

    if any("Skills section" in w for w in warnings):
        suggestions.append("Add a clearly labeled 'Skills' section near the top of the resume.")
    if any("Experience section" in w for w in warnings):
        suggestions.append("Add a clearly labeled 'Experience' or 'Work Experience' section.")
    if any("date styles" in w for w in warnings):
        suggestions.append("Use one consistent date format, such as 'Jan 2023 - Mar 2025'.")
    if any("Email address" in w for w in warnings):
        suggestions.append("Place your email near the top header in plain text.")
    if any("Phone number" in w for w in warnings):
        suggestions.append("Place your phone number near the top header in plain text.")
    if any("LinkedIn or GitHub" in w for w in warnings):
        suggestions.append("Add a LinkedIn profile URL and GitHub URL if relevant.")
    if any("Location" in w for w in warnings):
        suggestions.append("Add your city and country or city and state near the top.")
    if any("Decorative symbols" in w for w in warnings):
        suggestions.append("Remove decorative icons and symbols from headings and bullet areas.")
    if any("Pipe characters" in w for w in warnings):
        suggestions.append("Avoid overusing pipe separators. Use simple spacing or separate lines.")
    if any("very long lines" in w for w in warnings):
        suggestions.append("Break dense paragraphs into shorter bullet points.")
    if any("few bullet points" in w for w in warnings):
        suggestions.append("Use bullet points for accomplishments under each role.")
    if any("Tab-heavy formatting" in w for w in warnings):
        suggestions.append("Use standard spacing instead of tabs to improve parser compatibility.")

    if "summary" not in found_sections:
        suggestions.append("Consider adding a short professional summary tailored to the target role.")
    if "projects" not in found_sections:
        suggestions.append("Add a Projects section if you have relevant technical or portfolio work.")

    # Deduplicate while preserving order
    deduped = []
    seen = set()
    for item in suggestions:
        if item not in seen:
            deduped.append(item)
            seen.add(item)

    return deduped[:10]


def _score_from_warning_count(warnings: List[str], found_sections: List[str]) -> float:
    score = 100.0

    # Penalize warnings
    score -= len(warnings) * 6

    # Reward good structure
    strong_core = {"summary", "skills", "experience", "education"}
    score += len(strong_core.intersection(set(found_sections))) * 2

    return max(0.0, min(100.0, round(score, 1)))


def analyze_ats_readability(resume_text: str) -> Dict[str, Any]:
    lines = _normalize_lines(resume_text)
    found_sections = _find_sections(lines)

    contact_flags = {
        "email": _detect_email(resume_text),
        "phone": _detect_phone(resume_text),
        "linkedin": _detect_linkedin(resume_text),
        "github": _detect_github(resume_text),
        "location": _detect_location(resume_text),
    }

    date_strings = _extract_dates(resume_text)

    warnings = []
    warnings.extend(_section_warnings(found_sections))
    warnings.extend(_contact_warnings(resume_text))
    warnings.extend(_date_format_warnings(date_strings))
    warnings.extend(_special_character_warnings(resume_text))
    warnings.extend(_content_warnings(lines, resume_text))

    # Deduplicate warnings
    unique_warnings = []
    seen = set()
    for w in warnings:
        if w not in seen:
            unique_warnings.append(w)
            seen.add(w)

    improvements = _build_improvements(unique_warnings, found_sections)
    ats_score = _score_from_warning_count(unique_warnings, found_sections)

    if ats_score >= 85:
        verdict = "ATS-friendly"
    elif ats_score >= 70:
        verdict = "mostly ATS-friendly"
    elif ats_score >= 50:
        verdict = "needs ATS improvements"
    else:
        verdict = "high ATS risk"

    return {
        "ats_score": ats_score,
        "ats_verdict": verdict,
        "detected_sections": found_sections,
        "contact_checks": contact_flags,
        "format_warnings": unique_warnings[:12],
        "ats_improvements": improvements[:10],
    }