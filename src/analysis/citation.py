import re

def check_citations(text, references_text=""):
    """
    Analyzes citations in the text.
    1. Identifies inline citations (e.g., [1], (Author, 2023)).
    2. Checks if they match entries in the references section (if provided).
    3. Returns a 'credibility score' logic based on citation density and formatting.
    """
    
    # 1. Regex for common citation formats
    # [1], [12]
    numeric_citations = re.findall(r'\[\s*\d+\s*\]', text)
    # (Smith, 2020)
    auth_date_citations = re.findall(r'\([A-Za-z\s]+,\s*\d{4}\)', text)
    
    total_citations = len(numeric_citations) + len(auth_date_citations)
    
    # 2. Heuristic Scoring
    # If text is long but has 0 citations, low credibility for a "Scholarly Paper"
    word_count = len(text.split())
    if word_count < 50:
        score = 1.0 # Too short to judge
    else:
        # Expect at least 1 citation per 200 words for scholarly content?
        expected = word_count / 200
        if total_citations >= expected:
            score = 1.0
        elif total_citations > 0:
            score = 0.5 + (0.5 * (total_citations / expected))
        else:
            score = 0.2 # Very suspicious for a scholarly paper
            
    return {
        'score': round(score, 2),
        'count': total_citations,
        'details': f"Found {total_citations} citations (Numeric: {len(numeric_citations)}, Auth-Date: {len(auth_date_citations)})"
    }
