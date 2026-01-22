import os
import re


def check_plagiarism(text, corpus_dir):
    """Naive plagiarism check: finds exact sentence matches in text files under corpus_dir.
    Returns (score, matches)
    """
    if not text:
        return 0.0, []
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    corpus_text = ''
    if os.path.isdir(corpus_dir):
        for fname in os.listdir(corpus_dir):
            if fname.lower().endswith('.txt'):
                try:
                    with open(os.path.join(corpus_dir, fname), 'r', encoding='utf-8') as f:
                        corpus_text += f.read() + '\n'
                except Exception:
                    continue
    matches = []
    for s in sentences:
        # only consider longer sentences for match
        if len(s.split()) > 8 and s in corpus_text:
            matches.append(s)
    score = 0.0
    if sentences:
        score = min(1.0, len(matches) / max(1, len(sentences)))
    return round(score, 3), matches
