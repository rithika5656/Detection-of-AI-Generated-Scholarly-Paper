import os
import sys
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# make src importable when running from project root
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from extraction.extract import extract_text
from preprocessing.clean import preprocess
from analysis.ai_detector import detect_ai
from analysis.plagiarism import check_plagiarism
from analysis.citation import check_citations
from analysis.eligibility import check_eligibility  # New Import
from scoring.score import aggregate_scores
from report.generate import generate_report
from learning.retrain import retrain
from pydantic import BaseModel

app = FastAPI(title="Scholarly Paper Detector API")

# CORS - allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FeedbackRequest(BaseModel):
    filename: str
    is_accurate: bool
    comments: str = None

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / 'web'
UPLOAD_DIR = ROOT / 'data' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# mount static files (css/js)
if WEB_DIR.exists():
    app.mount('/static', StaticFiles(directory=str(WEB_DIR)), name='static')


@app.get('/')
def root():
    index_file = WEB_DIR / 'index.html'
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Web frontend not found. Place files in /web directory."}


@app.post('/analyze')
async def analyze(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    save_path = UPLOAD_DIR / file.filename
    try:
        content = await file.read()
        save_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    text, metadata = extract_text(str(save_path))
    
    if text.startswith("Error"):
        # Return a 422 Unprocessable Entity with the specific error message (e.g., Tesseract missing)
        raise HTTPException(status_code=422, detail=text)
        
    sections = preprocess(text)
    ai_result = detect_ai(sections.get('body',''))
    # Handle dict or float for backward compatibility (though we know it is dict now)
    ai_score_val = ai_result['score'] if isinstance(ai_result, dict) else ai_result
    
    plagiarism_score, matches = check_plagiarism(sections.get('body',''), str(ROOT / 'data'))
    
    citation_result = check_citations(sections.get('body', ''))
    
    # NEW: Check Eligibility
    eligibility_result = check_eligibility(
        ai_score_val,
        plagiarism_score,
        citation_result,
        sections.get('body','')
    )
    
    final = aggregate_scores(ai_score_val, plagiarism_score)
    
    # Add eligibility to the report structure
    report = generate_report(str(save_path), metadata, sections, ai_result, plagiarism_score, citation_result, final, matches)
    report['eligibility'] = eligibility_result # Append explicitly since generate_report might not expect it
    
    return report

@app.post('/feedback')
def submit_feedback(feedback: FeedbackRequest):
    """
    Collects user feedback for the learning loop.
    """
    # In a real app, this would save to a database.
    # Here we just log it and call the dummy retrain function.
    print(f"Feedback received: {feedback}")
    retrain(feedback.dict())
    return {"status": "received", "message": "Thank you for your feedback! This helps us improve."}


@app.get('/health')
def health():
    return {'status':'ok'}
