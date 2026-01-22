# Detection-of-AI-Generated-Scholarly-Paper

AI-Generated Scholarly Paper Detection System

This project is a machine learning–based system designed to identify whether an academic or research document is written by a human or generated using artificial intelligence. The system analyzes scholarly text using natural language processing and machine learning techniques to extract linguistic, statistical, and semantic features, and classifies the content based on learned academic writing patterns.

## Workflow
1. **Paper Upload**: Upload PDF/Text, extract main text, references, and metadata.
2. **Preprocessing**: Clean and normalize text, split into sections, collect author/citation details.
3. **Analysis**: Language analysis, AI text detection, plagiarism check, citation check.
4. **Scoring**: Generate and combine scores for AI-generation and plagiarism likelihood.
5. **Report Generation**: Detailed report with scores, highlights, and originality assessment.
6. **Decision**: Accept, Review Needed, or Reject based on scores.
7. **Learning Loop**: Collect reviewer feedback and retrain models for improved accuracy.

## Project Structure
- `data/` — Sample papers and test data
- `src/`
  - `extraction/` — PDF/text extraction modules
  - `preprocessing/` — Text cleaning and sectioning
  - `analysis/` — Language, AI, plagiarism, and citation analysis
  - `scoring/` — Score calculation and aggregation
  - `report/` — Report generation
  - `learning/` — Model retraining and feedback loop
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

## Contribution
Pull requests and feedback are welcome. Please open issues for suggestions or bugs.
