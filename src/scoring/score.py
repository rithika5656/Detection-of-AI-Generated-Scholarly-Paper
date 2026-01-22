def aggregate_scores(ai_score, plagiarism_score, weights=None):
    if weights is None:
        weights = {'ai': 0.6, 'plagiarism': 0.4}
    final_prob = ai_score * weights.get('ai', 0.6) + plagiarism_score * weights.get('plagiarism', 0.4)
    decision = 'Accept'
    if final_prob > 0.7:
        decision = 'Reject'
    elif final_prob > 0.3:
        decision = 'Review Needed'
    return {'final_probability': round(final_prob, 3), 'decision': decision}
