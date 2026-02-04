def aggregate_scores(ai_score, plagiarism_score, citation_score=1.0, weights=None):
    if weights is None:
        weights = {'ai': 0.5, 'plagiarism': 0.3, 'citation': 0.2}
    ai_val = ai_score['score'] if isinstance(ai_score, dict) else ai_score
    citation_val = citation_score if isinstance(citation_score, (int, float)) else 1.0
    # Citation score is positive (higher = better), so we invert for penalty
    citation_penalty = 1.0 - citation_val
    final_prob = ai_val * weights.get('ai', 0.5) + plagiarism_score * weights.get('plagiarism', 0.3) + citation_penalty * weights.get('citation', 0.2)
    decision = 'Accept'
    if final_prob > 0.7:
        decision = 'Reject'
    elif final_prob > 0.3:
        decision = 'Review Needed'
    return {'final_probability': round(final_prob, 3), 'decision': decision}
