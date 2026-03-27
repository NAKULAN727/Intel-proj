# Enterprise PDF Knowledge Base

Convert Enterprise PDFs into Searchable Knowledge using local AI models.

## Features

- **📄 Smart PDF Parsing**: Handles text, tables, and scanned sections (OCR).
- **🖼️ Multimodal**: Extracts images and generates captions using AI (BLIP).
- **📊 Table Extraction**: Stores tables in a separate NoSQL database (TinyDB).
- **🤖 Local RAG**: Fully local embedding and QA using ChromaDB and Flan-T5.
- **🖥️ Web Interface**: Clean Streamlit UI for searching and visualizing data.

## 🚀 Features (Upgraded)

- **📄 Hybrid Retrieval Engine**: Combines **BM25 keyword search** with **Dense vector search** (MiniLM) and a **Cross-Encoder reranker** for pinpoint accuracy.
- **🤖 High-Performance Local AI**: Run **Microsoft Phi-3 Mini (3.8B)** locally for document QA (fallback to Flan-T5).
- **📝 Semantic Chunking**: Smart sentence-boundary chunking that preserves context and page numbers for source attribution.
- **🖼️ Multimodal Extraction**: Higher resolution image captioning (150 DPI) using Salesforce BLIP.
- **📊 Table-to-RAG Integration**: Converts tables into searchable text representations for the RAG pipeline.
- **📌 Source Attribution**: Every answer shows clickable "Source Cards" with page number and relevance score.

## 🛠️ Setup & Installation

Follow these steps for a production-ready local setup (Python 3.10+):

### 1. Install Dependencies
```bash
# 1. Update pip
python -m pip install --upgrade pip

# 2. Install all core libraries
pip install -r requirements.txt

# 3. Install search & LLM specialized libraries
pip install rank-bm25 llama-cpp-python
```

### 2. Download the AI Model (Phi-3 Mini)
While the system includes a basic fallback, for the best quality, download the high-performance GGUF model:
1.  Go to [Phi-3-mini-4k-instruct-gguf](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf).
2.  Download `Phi-3-mini-4k-instruct-q4.gguf` (~2.4 GB).
3.  Place it in the `models/` folder: `Intel Ai Proj/models/phi3-mini-q4.gguf`.

### 3. OCR Support (Tesseract)
For scanned PDFs, you must have [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed:
-   **Windows**: Download the installer and ensure it is in `C:\Program Files\Tesseract-OCR\tesseract.exe`.

## 🖥️ How to Run
```bash
streamlit run app.py
```

## 🏗️ Architecture Stack (Local-Only)

1.  **Ingestion Engine**:
    -   `pdfplumber` + `pytesseract` (OCR) for text.
    -   `Salesforce/BLIP` for image intelligence.
    -   **New**: `SemanticChunker` for sentence-boundary aware splits.
2.  **Hybrid Retrieval**:
    -   `ChromaDB`: High-speed vector storage.
    -   `Rank-BM25`: Keyword-level retrieval index.
    -   `Cross-Encoder`: Reranks Top-12 merged candidates for the best answer.
3.  **Generation Pipeline**:
    -   `llama-cpp-python` (Phi-3 Mini 3.8B) for high-quality instruction following.
    -   `Streamlit` for an interactive, premium chat interface.

---
_Note: No data leaves your machine. No OpenAI/External API keys required._
