"""
PDF processing module with OCR and Table Extraction capabilities.
"""
import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import io
import os
from tinydb import TinyDB, Query
from image_captioning import ImageCaptioner

# Initialize NoSQL DB for tables
table_db = TinyDB('tables_db.json')

# Initialize Captioner (lazy load logic could be better, but initializing global for now)
try:
    captioner = ImageCaptioner()
except:
    captioner = None

def extract_text_and_tables(pdf_path, use_ocr=True):
    """
    Process PDF to extract text (with OCR fallback), tables, and image descriptions.
    """
    full_text = ""
    total_tables = 0
    total_images = 0
    
    try:
        # Use simple PyMuPDF for speed first check, but pdfplumber is main for features
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 Processing {len(pdf.pages)} pages...")
            
            for i, page in enumerate(pdf.pages):
                # 1. Try standard text extraction
                text = page.extract_text() or ""
                
                # 2. OCR Fallback
                if use_ocr and len(text.strip()) < 50:
                    print(f"⚠️ Page {i+1} seems scanned. Attempting OCR...")
                    try:
                        im = page.to_image(resolution=300)
                        text = pytesseract.image_to_string(im.original)
                    except Exception as e:
                        print(f"   OCR Failed: {e}")
                        
                # 3. Extract Tables
                tables = page.extract_tables()
                if tables:
                    for t_idx, table in enumerate(tables):
                        table_record = {
                            "file": os.path.basename(pdf_path),
                            "page": i + 1,
                            "table_index": t_idx,
                            "data": table
                        }
                        table_db.insert(table_record)
                        text += f"\n[TABLE_EXTRACTED_PAGE_{i+1}_ID_{t_idx}]\n"
                    total_tables += len(tables)

                # 4. Extract and Capability Images
                # pdfplumber images are dicts with bbox, etc.
                if captioner and captioner.ready:
                    for img in page.images:
                        try:
                            # Get image data. pdfplumber 'images' gives metadata.
                            # We use 'stream' to get data or crop from page.
                            # Cropping is safer to get exactly what's seen.
                            bbox = (img['x0'], img['top'], img['x1'], img['bottom'])
                            cropped_page = page.crop(bbox)
                            im_obj = cropped_page.to_image(resolution=72).original
                            
                            caption = captioner.generate_caption(im_obj)
                            print(f"   🖼️ Page {i+1} Image: {caption}")
                            text += f"\n[IMAGE_DESC: {caption}]\n"
                            total_images += 1
                        except Exception as e:
                            print(f"   Failed to caption image: {e}")

                full_text += f"\n\n{text}\n"

        print(f"✅ Extracted {total_tables} tables and filtered {total_images} images.")
        return full_text

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""

def chunk_text(text, chunk_size=1000, overlap=100):
    """
    Split text into chunks. 
    Updated to be larger (1000 chars) for better context in RAG.
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Adjust end to nearest whitespace to avoid splitting words
        if end < len(text):
            # Check for generic whitespace
            next_space = text.find(' ', end)
            if next_space != -1 and next_space - end < 50:
                end = next_space
                
        chunk = text[start:end]
        chunks.append(chunk.strip())
        
        start = end - overlap
        if start >= len(text):
            break
            
    return [c for c in chunks if c]
