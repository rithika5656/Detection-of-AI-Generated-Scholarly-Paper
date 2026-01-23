import os
import json
from flask import Flask, request, jsonify, render_template_string

# ensure src modules importable when running from repo root
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extraction.extract import extract_text
from preprocessing.clean import preprocess
from analysis.ai_detector import detect_ai
from analysis.plagiarism import check_plagiarism
from scoring.score import aggregate_scores
from report.generate import generate_report

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WEB_DIR = os.path.join(BASE_DIR, 'web')
app = Flask(__name__, static_folder=WEB_DIR, static_url_path='/static', template_folder=WEB_DIR)
UPLOAD_DIR = os.path.join('data', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
        return app.send_static_file('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    f = request.files.get('file')
    if not f:
        return jsonify({'error':'no file provided'}), 400
    filename = f.filename or 'upload'
    save_path = os.path.join(UPLOAD_DIR, filename)
    f.save(save_path)

    text, metadata = extract_text(save_path)
    sections = preprocess(text)
    ai_score = detect_ai(sections.get('body',''))
    plagiarism_score, matches = check_plagiarism(sections.get('body',''), 'data')
    final = aggregate_scores(ai_score, plagiarism_score)
    report = generate_report(save_path, metadata, sections, ai_score, plagiarism_score, final, matches)

    return jsonify(report)

if __name__ == '__main__':
    app.run(debug=True)
