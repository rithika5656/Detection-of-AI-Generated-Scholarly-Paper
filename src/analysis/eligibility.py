def check_eligibility(ai_score, plagiarism_score, citation_score, text):
    """
    Determines if the candidate is eligible for a scholarship based on:
    1. Originality (Low AI, Low Plagiarism)
    2. Research Quality (High Citation score)
    3. Data Integrity (No markers of fake/hallucinated data)
    """
    
    reasons = []
    is_eligible = True
    integrity_score = 1.0 # Start with perfect trust
    
    # 1. AI Threshold (Strict for Scholarships)
    if ai_score > 0.25: # > 25% AI
        is_eligible = False
        reasons.append(f"AI Content detected ({int(ai_score*100)}%). Scholarship requires >75% human authorship.")
        integrity_score -= 0.4
    
    # 2. Plagiarism Threshold
    if plagiarism_score > 0.15: # > 15% Plagiarism
        is_eligible = False
        reasons.append(f"Plagiarism detected ({int(plagiarism_score*100)}%). Academic integrity check failed.")
        integrity_score -= 0.3

    # 3. Citation/Quality Check
    cit_val = citation_score.get('score', 0)
    if cit_val < 0.5:
        is_eligible = False
        reasons.append("Insufficient citation credibility. Research quality does not meet scholarship standards.")
        integrity_score -= 0.2
        
    # 4. Data Integrity / Fake Data Heuristics
    # Scanning for signs of "hallucinated" or low-effort generic data
    lower_text = text.lower()
    suspicious_phrases = [
        "synthetic data", "generated dataset", "simulated values", "randomly generated",
        "as an ai language model", "sample text", "lorem ipsum"
    ]
    
    found_suspicious = [p for p in suspicious_phrases if p in lower_text[:5000]] # check first 5k chars
    if found_suspicious:
        is_eligible = False
        reasons.append(f"Potential unoriginal/synthetic data detected: '{found_suspicious[0]}'.")
        integrity_score -= 0.5
        
    return {
        'is_eligible': is_eligible,
        'integrity_score': max(0.0, round(integrity_score, 2)),
        'reasons': reasons
    }
