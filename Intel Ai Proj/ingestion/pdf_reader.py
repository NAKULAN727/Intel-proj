"""
PDF reader: structured per-page extraction with OCR fallback,
table-to-text injection, and BLIP image captioning.

Returns a list of page dicts instead of a single string —
enabling page-level metadata for source attribution.
"""
import pdfplumber
import pytesseract
from tinydb import TinyDB, Query
from ingestion.image_captioner import ImageCaptioner
from ingestion.table_extractor import table_to_text
import os


# Storage for raw table data
_table_db = None


def get_table_db() -> TinyDB:
    global _table_db
    if _table_db is None:
        os.makedirs("storage", exist_ok=True)
        _table_db = TinyDB("storage/tables_db.json")
    return _table_db


def extract_pages(pdf_path: str, use_ocr: bool = True) -> list:
    """
    Extract all pages from a PDF, returning rich structured data per page.

    Args:
        pdf_path: Path to PDF file
        use_ocr: Whether to use Tesseract OCR for low-text pages

    Returns:
        List of {"page": int, "text": str, "source": str}
    """
    pages_data = []
    source = os.path.basename(pdf_path)
    db = get_table_db()

    # Clear previous records for this file
    FileQ = Query()
    db.remove(FileQ.file == source)

    # Lazy-load captioner (avoid startup cost if PDF has no images)
    captioner = ImageCaptioner()

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Processing {len(pdf.pages)} pages from '{source}'...")

        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            text = page.extract_text() or ""

            # --- OCR Fallback ---
            if use_ocr and len(text.strip()) < 50:
                try:
                    print(f"  Page {page_num}: sparse text, trying OCR...")
                    im = page.to_image(resolution=300)
                    text = pytesseract.image_to_string(im.original)
                except Exception as e:
                    print(f"  OCR failed page {page_num}: {e}")

            # --- Table Extraction ---
            # Tables are stored in TinyDB AND injected as readable text into the page
            tables = page.extract_tables()
            for t_idx, table in enumerate(tables):
                if not table:
                    continue
                text_repr = table_to_text(table, page_num)
                db.insert({
                    "file": source,
                    "page": page_num,
                    "table_index": t_idx,
                    "data": table,
                    "text_repr": text_repr
                })
                # Inject table text so it gets chunked and embedded
                text += f"\n{text_repr}\n"

            # --- Image Captioning (150 DPI for better quality) ---
            if captioner.ready and page.images:
                for img in page.images:
                    try:
                        bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                        cropped = page.crop(bbox)
                        # 150 DPI is 2x the original 72 DPI for better BLIP accuracy
                        im_obj = cropped.to_image(resolution=150).original
                        caption = captioner.generate_caption(im_obj)
                        if caption and "Error" not in caption:
                            text += f"\n[Image on page {page_num}: {caption}]\n"
                    except Exception as e:
                        print(f"  Image processing failed page {page_num}: {e}")

            # --- Context Cleaning ---
            cleaned_lines = []
            import re
            for line in text.split("\n"):
                lower_line = line.lower().strip()
                # Remove noisy lines
                if "image on page" in lower_line:
                    continue
                # Remove repeated headers/footers (e.g., short page numbers, dates)
                if len(lower_line) < 15 and (lower_line.startswith("page ") or lower_line.isdigit() or re.match(r'^\d{2}/\d{2}/\d{4}$', lower_line)):
                    continue
                if "irrelevant instruction" in lower_line or "do not write below" in lower_line:
                    continue
                cleaned_lines.append(line)
                
            clean_text = "\n".join(cleaned_lines)

            pages_data.append({
                "page": page_num,
                "text": clean_text,
                "source": source
            })

    total_tables = db.search(FileQ.file == source)
    print(f"Done: {len(pages_data)} pages, {len(total_tables)} tables extracted.")
    return pages_data
