import os
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the embedding model once at module level to avoid reloading it for every function call.
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
_model = SentenceTransformer(MODEL_NAME)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    numerator = np.dot(vec_a, vec_b)
    denominator = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def score_resume_vs_job(resume_text: str, job_description: str) -> float:
    """
    Returns a score from 0 to 100.
    """
    texts = [resume_text, job_description]
    embeddings = _model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    resume_embedding = embeddings[0]
    jd_embedding = embeddings[1]

    similarity = cosine_similarity(resume_embedding, jd_embedding)

    # similarity is approximately in [-1, 1], but in normal semantic text matching it is usually [0, 1]
    # clamp to [0, 1] for scoring safety
    similarity = max(0.0, min(1.0, similarity))

    return round(similarity * 100, 2)