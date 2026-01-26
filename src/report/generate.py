import json
import os


def generate_report(path, metadata, sections, ai_score, plagiarism_score, citation_score, final, matches):
    report = {
        'file': path,
        'metadata': metadata,
        'sections': sections,
        'scores': {
            'ai_score': ai_score,
            'plagiarism_score': plagiarism_score,
            'citation_score': citation_score,
            'final': final
        },
        'matches': matches,
        'summary': f"AI score {ai_score}, Plagiarism {plagiarism_score}, Citations {citation_score.get('score', 0)}, Decision: {final['decision']}"
    }
    out = os.path.join('data', 'report.json')
    try:
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
    except Exception:
        pass
    return report
