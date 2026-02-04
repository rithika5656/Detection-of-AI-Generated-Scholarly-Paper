from extraction.extract import extract_text
from preprocessing.clean import preprocess
from analysis.ai_detector import detect_ai
from analysis.plagiarism import check_plagiarism
from analysis.citation import check_citations
from scoring.score import aggregate_scores
from report.generate import generate_report


def main():
    path = "data/sample_paper.txt"
    text, metadata = extract_text(path)
    sections = preprocess(text)
    ai_score = detect_ai(sections.get('body',''))
    plagiarism_score, matches = check_plagiarism(sections.get('body',''), 'data')
    citation_score = check_citations(sections.get('body',''), sections.get('references',''))
    final = aggregate_scores(ai_score, plagiarism_score, citation_score.get('score', 1.0))
    report = generate_report(path, metadata, sections, ai_score, plagiarism_score, citation_score, final, matches)
    print(report['summary'])


if __name__ == "__main__":
    main()
