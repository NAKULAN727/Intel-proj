# Enterprise PDF Knowledge Base

Convert Enterprise PDFs into Searchable Knowledge using local AI models.

## Features

- **📄 Smart PDF Parsing**: Handles text, tables, and scanned sections (OCR).
- **🖼️ Multimodal**: Extracts images and generates captions using AI (BLIP).
- **📊 Table Extraction**: Stores tables in a separate NoSQL database (TinyDB).
- **🤖 Local RAG**: Fully local embedding and QA using ChromaDB and Flan-T5.
- **🖥️ Web Interface**: Clean Streamlit UI for searching and visualizing data.

## Setup

1. **Easy Start**:
   Simply run the `run_project.bat` file in the root directory. It will install dependencies and start the app.

2. **Manual Setup**:
   If you prefer manual commands:
   ```bash
   py -m pip install -r requirements.txt
   py -m streamlit run app.py
   ```

_Note: For OCR to work, you must have [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on your system._

## How it works

1. **Ingestion**:
   - `pdfplumber` extracts layout-aware text.
   - `pytesseract` handles low-quality/scanned scans.
   - `BLIP` models generate descriptions for images.
2. **Storage**:
   - Text chunks -> ChromaDB (Vector Store).
   - Tables -> TinyDB (JSON Document Store).
3. **Retrieval**:
   - Hybrid search over text and image descriptions.
   - Interactive chat using Streamlit.

## Models Used

- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **LLM**: google/flan-t5-base
- **Image Captioning**: Salesforce/blip-image-captioning-base
