# PDF Knowledge Base

Convert Enterprise PDFs into Searchable Knowledge using local AI models.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your PDF file as `sample.pdf` in the project directory.

3. Run the system:
```bash
python main.py
```

## How it works

1. **PDF Text Extraction**: Extracts all readable text from the PDF
2. **Text Chunking**: Splits text into overlapping chunks for better context
3. **Vector Embeddings**: Generates embeddings using sentence-transformers
4. **Vector Database**: Stores embeddings in local ChromaDB
5. **Question Answering**: Uses local Flan-T5 model to answer questions

## Features

- ✅ Fully local - no API keys required
- ✅ Works offline after initial model download
- ✅ Command-line interface
- ✅ Persistent vector database
- ✅ Semantic search with embeddings

## Models Used

- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **LLM**: google/flan-t5-base

Models will be downloaded automatically on first run.