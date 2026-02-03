# Detection-of-AI-Generated-Scholarly-Paper

AI-Generated Scholarly Paper Detection System with Chatbot Integration

This project is a machine learning–based system designed to identify whether an academic or research document is written by a human or generated using artificial intelligence. The system analyzes scholarly text using natural language processing and machine learning techniques to extract linguistic, statistical, and semantic features, and classifies the content based on learned academic writing patterns.

## ✨ Key Features

### GenAI-Specific Detection
The system extracts features characteristic of different Large Language Models:
- **GPT-style Repetition**: Detects formulaic phrases typical of GPT models
- **Gemini Explanatory Overflow**: Identifies over-explanation patterns
- **Claude Uncertainty Hedging**: Detects hedging language patterns
- **Low Burstiness (OpenLLM)**: Measures sentence length variance
- **Citation Hallucination**: Identifies potentially fabricated references
- **Perplexity-based Measures**: Estimates text predictability

### Explainable AI Chatbot
An integrated chatbot that:
- Explains detection scores and their meaning
- Provides educational context about AI-generated text characteristics
- Answers questions about the detection methodology
- Offers guidance for improving human-written content

**Important**: The chatbot is designed ONLY to explain results. It does NOT generate academic content or assist in bypassing detection.

## Workflow
1. **Paper Upload**: Upload PDF/Text, extract main text, references, and metadata.
2. **Preprocessing**: Clean and normalize text, split into sections, collect author/citation details.
3. **Analysis**: Language analysis, AI text detection, plagiarism check, citation check.
4. **GenAI Feature Extraction**: Extract GPT, Gemini, Claude patterns + burstiness/perplexity.
5. **Scoring**: Generate and combine scores for AI-generation and plagiarism likelihood.
6. **Report Generation**: Detailed report with scores, highlights, and originality assessment.
7. **Chatbot Explanation**: AI assistant explains results in human-readable format.
8. **Decision**: Accept, Review Needed, or Reject based on scores.
9. **Learning Loop**: Collect reviewer feedback and retrain models for improved accuracy.

## Project Structure
- `data/` — Sample papers and test data
- `src/`
  - `extraction/` — PDF/text extraction modules
  - `preprocessing/` — Text cleaning and sectioning
  - `analysis/` — Language, AI, plagiarism, and citation analysis
    - `genai_features.py` — GenAI-specific feature extraction
  - `chatbot/` — Explainable AI chatbot module
    - `explainer.py` — Chatbot logic and responses
  - `scoring/` — Score calculation and aggregation
  - `report/` — Report generation
  - `learning/` — Model retraining and feedback loop
- `web/` — Frontend files (HTML, CSS, JavaScript)
- `requirements.txt` — Python dependencies
- `README.md` — Project overview and setup instructions

## Setup
1. Install Python 3.9+
2. Install dependencies: `pip install -r requirements.txt`
3. Run the main pipeline (to be implemented)

## Usage
- Place sample papers in the `data/` folder.
- Run the main script (to be provided) to process and analyze papers.

## API Prototype (FastAPI)
1. Install dependencies: `pip install -r requirements.txt`
2. Run the API locally with Uvicorn:

```bash
uvicorn src.api:app --reload
```

3. Open http://127.0.0.1:8000/ and upload a `.txt` or `.pdf` file to analyze.

There is also an automated test that posts the included `data/sample_paper.txt` to the API endpoint:

```bash
python src/run_api_test.py
```

## Frontend
The project includes a simple static frontend served by the API. After starting the API, open:

```
http://127.0.0.1:8000/
```

The frontend lets you upload a `.txt` or `.pdf` file and shows the analysis results.

## 🤖 Chatbot Integration

The chatbot appears as a floating button in the bottom-right corner. Click to open and:
- Ask about your detection scores
- Learn what features like "perplexity" and "burstiness" mean
- Get writing improvement tips
- Understand the detection methodology

### Example Questions:
- "Explain my scores"
- "What is perplexity?"
- "Why was my paper flagged?"
- "How can I improve my writing?"

### API Endpoints for Chatbot:
- `POST /chat` — Send a message to the chatbot
- `GET /chat/greeting` — Get initial greeting
- `POST /chat/explain` — Generate explanation for analysis result

## 📊 GenAI Features API

The detection now returns detailed GenAI-specific features:

```json
{
  "genai_features": {
    "composite_score": 0.45,
    "features": {
      "gpt_repetition": {"score": 0.3, "details": {...}},
      "gemini_overflow": {"score": 0.2, "details": {...}},
      "claude_hedging": {"score": 0.4, "details": {...}},
      "burstiness": {"score": 0.5, "details": {...}},
      "citation_hallucination": {"score": 0.1, "details": {...}},
      "perplexity": {"score": 0.6, "details": {...}}
    },
    "interpretation": ["High Low perplexity (predictable text) detected"]
  }
}
```

## Contribution
Pull requests and feedback are welcome. Please open issues for suggestions or bugs.

## Ethical Notice

This system is designed to support academic integrity, not to enable circumvention. The chatbot will refuse requests to:
- Generate academic content
- Help bypass detection systems
- Assist in any form of academic dishonesty
