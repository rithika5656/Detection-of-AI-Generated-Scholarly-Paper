import os

def extract_text(path):
    """Extract text from .txt, .pdf, or image files (.png, .jpg, .jpeg).
    Returns (text, metadata)
    """
    metadata = {'title': os.path.basename(path)}
    text = ""
    ext = os.path.splitext(path)[1].lower()
    
    try:
        if ext == '.pdf':
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(path)
                pages = [p.extract_text() for p in reader.pages]
                text = "\n".join(p for p in pages if p)
            except Exception:
                # Fallback to OCR for PDF if needed (not implemented to keep simple)
                pass
                
        elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            try:
                from PIL import Image
                import pytesseract
                # Attempt OCR
                image = Image.open(path)
                text = pytesseract.image_to_string(image)
            except ImportError:
                text = "Error: Missing libraries (Pillow or pytesseract)."
            except Exception as e:
                # specific error for missing tesseract binary
                if "tesseract is not installed" in str(e).lower() or "not found" in str(e).lower():
                     text = "Error: Tesseract OCR is not installed or not in PATH. Please install Tesseract-OCR."
                else:
                    text = f"Error extracting text from image: {e}"
                    
        else:
            # Assume text file
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
                
    except Exception as e:
        text = f"Error reading file: {e}"
        
    return text, metadata
