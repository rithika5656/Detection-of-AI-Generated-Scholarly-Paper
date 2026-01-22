import os

def extract_text(path):
    """Extract text from a plain .txt file or a PDF (if PyPDF2 is available).
    Returns (text, metadata)
    """
    metadata = {'title': os.path.basename(path)}
    text = ""
    try:
        if path.lower().endswith('.pdf'):
            try:
                from PyPDF2 import PdfReader
            except Exception:
                raise
            reader = PdfReader(path)
            pages = [p.extract_text() for p in reader.pages]
            text = "\n".join(p for p in pages if p)
        else:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
    except Exception:
        # fallback: return empty text but keep metadata
        text = ""
    return text, metadata
