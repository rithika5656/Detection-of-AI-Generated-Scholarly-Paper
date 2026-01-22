import re


def detect_ai(text):
    """Heuristic AI-likelihood score between 0.0 and 1.0.
    This is a placeholder; replace with an ML model for production.
    """
    if not text or not text.strip():
        return 0.0
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = text.split()
    if not sentences or not words:
        return 0.0
    avg_len = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
    unique_ratio = len(set(words)) / max(1, len(words))
    # heuristic: longer sentences and lower lexical diversity -> higher AI score
    score = (avg_len / 30.0) * (1.0 - unique_ratio)
    score = max(0.0, min(1.0, score))
    return round(score, 3)
