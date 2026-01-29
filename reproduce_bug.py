
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath('src'))

from extraction.extract import extract_text
from preprocessing.clean import preprocess
from analysis.ai_detector import detect_ai
from analysis.plagiarism import check_plagiarism
from scoring.score import aggregate_scores
from report.generate import generate_report

file_path = 'data/uploads/debug_test.xlsx'

print(f"Testing extraction on {file_path}...")
try:
    text, metadata = extract_text(file_path)
    print(f"Extracted text: {text[:100]}...")
except Exception as e:
    print(f"CRASH in extract_text: {e}")
    sys.exit(1)

print("Testing preprocessing...")
try:
    sections = preprocess(text)
    print(f"Sections keys: {sections.keys()}")
except Exception as e:
    print(f"CRASH in preprocess: {e}")
    sys.exit(1)

print("Testing AI detection...")
try:
    ai_score = detect_ai(sections.get('body',''))
    print(f"AI Score: {ai_score}")
except Exception as e:
    print(f"CRASH in detect_ai: {e}")
    sys.exit(1)

print("Testing Plagiarism...")
try:
    import pandas as pd # Ensure pandas is available for plagiarism if needed
    plagiarism_score, matches = check_plagiarism(sections.get('body',''), 'data')
    print(f"Plagiarism Score: {plagiarism_score}")
except Exception as e:
    print(f"CRASH in check_plagiarism: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
    
print("Testing Report Generation...")
try:
    final = aggregate_scores(ai_score, plagiarism_score)
    report = generate_report(file_path, metadata, sections, ai_score, plagiarism_score, final, matches)
    print("Report generated successfully.")
except Exception as e:
    print(f"CRASH in generate_report: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
