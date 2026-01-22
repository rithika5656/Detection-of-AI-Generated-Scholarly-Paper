from extraction.extract import extract_text
from preprocessing.clean import preprocess
from analysis.ai_detector import detect_ai
from analysis.plagiarism import check_plagiarism
from scoring.score import aggregate_scores
from report.generate import generate_report


def main():
    path = "data/sample_paper.txt"
    text, metadata = extract_text(path)
    sections = preprocess(text)
    ai_score = detect_ai(sections.get('body',''))
    plagiarism_score, matches = check_plagiarism(sections.get('body',''), 'data')
    final = aggregate_scores(ai_score, plagiarism_score)
    report = generate_report(path, metadata, sections, ai_score, plagiarism_score, final, matches)
    print(report['summary'])


if __name__ == "__main__":
    main()
