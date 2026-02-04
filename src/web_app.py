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
from analysis.citation import check_citations
from scoring.score import aggregate_scores
from report.generate import generate_report
from chatbot.explainer import ExplainerChatbot

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Initialize chatbot
chatbot = ExplainerChatbot()
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
    citation_score = check_citations(sections.get('body',''), sections.get('references',''))
    plagiarism_score, matches = check_plagiarism(sections.get('body',''), 'data')
    final = aggregate_scores(ai_score, plagiarism_score)
    report = generate_report(save_path, metadata, sections, ai_score, plagiarism_score, citation_score, final, matches)

    return jsonify(report)

@app.route('/chat/greeting', methods=['GET'])
def chat_greeting():
    """Return initial chatbot greeting."""
    return jsonify({
        'message': "Hello! I'm your Detection Assistant. Upload a paper to analyze, then ask me about the results!"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    user_message = data.get('message', '')
    analysis_context = data.get('analysis_context', None)
    
    # Get response from chatbot
    response = chatbot.get_response(user_message, analysis_context)
    
    return jsonify({'message': response.get('message', '')})

if __name__ == '__main__':
    app.run(debug=True)
