from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

router = APIRouter()

@router.post("/query")
async def ask_question(request: Request, body: QueryRequest):
    query = body.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    engine = getattr(request.app.state, "engine", None)
    if not engine:
        raise HTTPException(status_code=500, detail="Engine not loaded yet")

    try:
        answer, sources = engine.answer_question(query)
        return {
            "answer": answer,
            "sources": sources
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
