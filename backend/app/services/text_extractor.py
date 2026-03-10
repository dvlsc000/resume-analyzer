from pathlib import Path
from pypdf import PdfReader
from docx import Document
import textract


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages).strip()


def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def extract_text_from_doc(file_path: str) -> str:
    # textract can read old .doc files but may need system deps on some machines
    raw = textract.process(file_path)
    return raw.decode("utf-8", errors="ignore").strip()


def extract_resume_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".doc":
        return extract_text_from_doc(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF, DOC, and DOCX are allowed.")


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = " ".join(text.split())
    return text.strip()