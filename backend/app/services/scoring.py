def combine_scores(embedding_score: float, gemini_score: float) -> float:
    """
    Weighted hybrid score.
    You can adjust these weights later.
    """
    final_score = (0.4 * embedding_score) + (0.6 * gemini_score)
    return round(final_score, 2)


def get_verdict_from_score(score: float) -> str:
    if score >= 81:
        return "excellent match"
    elif score >= 61:
        return "strong match"
    elif score >= 41:
        return "moderate match"
    elif score >= 21:
        return "weak match"
    return "poor match"