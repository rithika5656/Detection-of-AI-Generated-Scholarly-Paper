import os
import re
import joblib
import numpy as np

# Path to the trained model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, 'data', 'models', 'ai_detector_rf.joblib')

# Load model globally to avoid reloading on every request
MODEL = None
try:
    if os.path.exists(MODEL_PATH):
        MODEL = joblib.load(MODEL_PATH)
        print(f"Loaded Random Forest model from {MODEL_PATH}")
    else:
        print(f"Model file not found at {MODEL_PATH}. Using heuristics.")
except Exception as e:
    print(f"Error loading model: {e}")

def detect_ai(text):
    """
    Detects AI probability using a Random Forest model if available,
    otherwise falls back to heuristics.
    """
    if not text or not text.strip():
        return {'score': 0.0, 'metrics': {'perplexity': 0, 'burstiness': 0}}
        
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = text.split()
    
    if not sentences or not words:
        return {'score': 0.0, 'metrics': {'perplexity': 0, 'burstiness': 0}}

    # Default Heuristic Calculation (Fallback & Metrics)
    avg_len = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
    unique_ratio = len(set(words)) / max(1, len(words))
    
    # 1. Try ML Model Prediction
    if MODEL:
        try:
            # Model pipeline expects a list/iterable of strings
            # predict_proba returns [[prob_human, prob_ai]]
            # We want prob_ai (index 1)
            prediction = MODEL.predict_proba([text])
            score = float(prediction[0][1])
        except Exception as e:
            print(f"Prediction error: {e}")
            # Fallback to heuristic
            heuristic_raw = (avg_len / 30.0) * (1.0 - unique_ratio)
            score = max(0.0, min(1.0, heuristic_raw))
    else:
        # Fallback Heuristic
        heuristic_raw = (avg_len / 30.0) * (1.0 - unique_ratio)
        score = max(0.0, min(1.0, heuristic_raw))
    
    # 2. Calculate Display Metrics (Perplexity/Burstiness proxy)
    # These are illustrative metrics for the UI since TF-IDF RF doesn't output them directly
    perplexity = int((1.0 - score) * 100) + 10 
    burstiness = int(unique_ratio * 100)
    
    return {
        'score': round(score, 3),
        'metrics': {
            'perplexity': perplexity,
            'burstiness': burstiness,
            'avg_sentence_len': round(avg_len, 1),
            'method': 'Random Forest' if MODEL else 'Heuristic'
        }
    }
