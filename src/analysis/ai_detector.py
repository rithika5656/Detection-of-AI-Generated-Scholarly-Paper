import re


def detect_ai(text):
    """Heuristic AI-likelihood score between 0.0 and 1.0.
    Returns a dictionary with score and detailed metrics.
    """
    if not text or not text.strip():
        return {'score': 0.0, 'metrics': {'perplexity': 0, 'burstiness': 0}}
    
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = text.split()
    
    if not sentences or not words:
        return {'score': 0.0, 'metrics': {'perplexity': 0, 'burstiness': 0}}
        
    avg_len = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
    unique_ratio = len(set(words)) / max(1, len(words))
    
    # heuristic: longer sentences and lower lexical diversity -> higher AI score
    raw_score = (avg_len / 30.0) * (1.0 - unique_ratio)
    score = max(0.0, min(1.0, raw_score))
    
    # Simulate advanced metrics based on heuristics for UI demo
    perplexity = int((1.0 - score) * 100) + 10  # Inverse to AI score
    burstiness = int(unique_ratio * 100)        # Correlated with diversity
    
    return {
        'score': round(score, 3),
        'metrics': {
            'perplexity': perplexity,
            'burstiness': burstiness,
            'avg_sentence_len': round(avg_len, 1)
        }
    }
