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
                
                # Auto-configure tesseract path if not in PATH
                tess_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
                    os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
                ]
                
                # Check if tesseract is in path by trying to run it? No, tesseract_cmd is better.
                # If the default fails, we might miss it, so let's pre-emptively set it if found and necessary.
                if not os.access(pytesseract.pytesseract.tesseract_cmd, os.X_OK) and 'tesseract' not in pytesseract.pytesseract.tesseract_cmd.lower():
                     # It's usually 'tesseract' by default. verification is hard without shutil.which
                     pass
                     
                for tp in tess_paths:
                    if os.path.exists(tp):
                        pytesseract.pytesseract.tesseract_cmd = tp
                        break
                        
                # Attempt OCR
                image = Image.open(path)
                text = pytesseract.image_to_string(image)
                
                if not text.strip():
                     text = "[OCR Warning]: No text found in image. It might be blurry or contain no text."
                     
            except ImportError:
                text = "Error: Missing libraries (Pillow or pytesseract)."
            except Exception as e:
                # specific error for missing tesseract binary
                if "tesseract is not installed" in str(e).lower() or "not found" in str(e).lower():
                     text = "Error: Tesseract OCR is not installed or not in PATH. Please install Tesseract-OCR."
                else:
                    text = f"Error extracting text from image: {e}"
                    
        elif ext in ['.xlsx', '.xls', '.csv']:
            import pandas as pd
            try:
                if ext == '.csv':
                    df = pd.read_csv(path)
                else:
                    df = pd.read_excel(path)
                
                # Convert all cells to string and join them
                text = "\n".join(df.astype(str).apply(lambda x: ' '.join(x), axis=1))
            except Exception as e:
                text = f"Error extracting text from spreadsheet: {e}"

        else:
            # Assume text file
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
                
    except Exception as e:
        text = f"Error reading file: {e}"
        
    return text, metadata
