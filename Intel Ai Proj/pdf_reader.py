"""
PDF text extraction module using PyMuPDF
"""
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """Extract all text from PDF file"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
        
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks for better context"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Find last sentence boundary to avoid cutting mid-sentence
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            boundary = max(last_period, last_newline)
            if boundary > start + chunk_size // 2:
                end = start + boundary + 1
                chunk = text[start:end]
        
        chunks.append(chunk.strip())
        start = end - overlap
        
        if start >= len(text):
            break
    
    return [chunk for chunk in chunks if chunk]