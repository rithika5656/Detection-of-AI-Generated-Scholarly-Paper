import os
import sys
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional

# make src importable when running from project root
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from extraction.extract import extract_text
from preprocessing.clean import preprocess
from analysis.ai_detector import detect_ai
from analysis.plagiarism import check_plagiarism
from analysis.citation import check_citations
from analysis.eligibility import check_eligibility  # New Import
from analysis.genai_features import extract_genai_features  # GenAI Feature Extraction
from scoring.score import aggregate_scores
from report.generate import generate_report
from learning.retrain import retrain
from chatbot.explainer import chat, generate_explanation, get_chatbot  # Chatbot Integration
from pydantic import BaseModel

app = FastAPI(
    title="Scholarly Paper Detector API",
    description="AI-Generated Scholarly Paper Detection System with Chatbot Integration",
    version="2.0.0"
)

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


class ChatRequest(BaseModel):
    """Request model for chatbot interactions."""
    message: str
    analysis_context: Optional[dict] = None  # Optional analysis result for context


class ChatResponse(BaseModel):
    """Response model for chatbot interactions."""
    message: str
    type: str
    intent: str


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
        
    try:
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
        
        # Add GenAI features to report for frontend display
        if isinstance(ai_result, dict) and 'genai_features' in ai_result:
            report['scores']['genai_features'] = ai_result['genai_features']
        
        # Generate automatic chatbot explanation
        try:
            report['chatbot_explanation'] = generate_explanation(report)
        except Exception as chat_err:
            print(f"Chatbot explanation error: {chat_err}")
            report['chatbot_explanation'] = "Analysis complete. Ask me about your results!"
        
        return report
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=f"Analysis failed: {str(e)}")

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


# ==================== CHATBOT ENDPOINTS ====================

@app.post('/chat', response_model=ChatResponse)
def chatbot_endpoint(request: ChatRequest):
    """
    Chatbot endpoint for explaining detection results.
    
    The chatbot can:
    - Explain detection scores and features
    - Answer questions about methodology
    - Provide writing improvement tips
    - Educate about AI-generated content detection
    
    ETHICAL NOTE: The chatbot will NOT help generate academic content
    or assist in bypassing detection systems.
    """
    try:
        response = chat(request.message, request.analysis_context)
        return ChatResponse(
            message=response.get('message', 'I could not process your request.'),
            type=response.get('type', 'unknown'),
            intent=response.get('intent', 'unknown')
        )
    except Exception as e:
        print(f"Chatbot error: {e}")
        return ChatResponse(
            message="I'm having trouble processing your request. Please try again.",
            type="error",
            intent="error"
        )


@app.get('/chat/greeting')
def chatbot_greeting():
    """
    Get the initial chatbot greeting message.
    """
    response = chat("hello")
    return {
        "message": response.get('message', 'Hello! How can I help you understand your analysis results?'),
        "suggestions": [
            "Explain my scores",
            "What is perplexity?",
            "How does detection work?",
            "Tips for better writing"
        ]
    }


@app.post('/chat/explain')
def chatbot_explain_analysis(analysis_result: dict):
    """
    Generate an automatic explanation for an analysis result.
    
    This endpoint is useful for generating explanations
    immediately after analysis is complete.
    """
    try:
        explanation = generate_explanation(analysis_result)
        return {
            "explanation": explanation,
            "status": "success"
        }
    except Exception as e:
        print(f"Explanation generation error: {e}")
        return {
            "explanation": "Analysis complete. Feel free to ask questions about your results!",
            "status": "fallback"
        }


@app.get('/health')
def health():
    return {'status':'ok'}
