from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import os
import shutil

router = APIRouter()

@router.post("/upload")
async def upload_document(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save PDF
    os.makedirs("storage", exist_ok=True)
    pdf_path = os.path.join("storage", file.filename)
    
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        from ingestion.pdf_reader import extract_pages
        from ingestion.chunker import semantic_chunk
        from retrieval.vector_store import VectorStore
        from retrieval.bm25_store import BM25Store

        print(f"Extracting pages from {file.filename}...")
        pages = extract_pages(pdf_path)
        if not pages or all(len(p["text"].strip()) == 0 for p in pages):
            raise HTTPException(status_code=400, detail="No text extracted. Scanned PDF?")

        print("Chunking into semantic units...")
        chunks = semantic_chunk(pages)
        if not chunks:
            raise HTTPException(status_code=400, detail="Chunking produced no results.")

        # Re-build indexes
        print("Building vector index...")
        vs = VectorStore()
        vs.clear()
        vs.add_documents(chunks)

        print("Building BM25 index...")
        bm25 = BM25Store()
        bm25.build(chunks)
        
        # If engine is already loaded, update its retriever instances
        if hasattr(request.app.state, "engine"):
            request.app.state.engine.retriever.vector_store = vs
            request.app.state.engine.retriever.bm25_store = bm25

        return {
            "message": "Upload successful and knowledge base built.",
            "filename": file.filename,
            "chunks_count": len(chunks)
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/documents")
async def list_documents():
    if not os.path.exists("storage"):
        return {"documents": []}
    
    files = [f for f in os.listdir("storage") if f.endswith(".pdf")]
    return {"documents": files}
