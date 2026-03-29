from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import document_routes, query_routes
from generation.llm_engine import PDFQueryEngine

app = FastAPI(title="Enterprise PDF Knowledge Base API", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load engine on startup to avoid reloading per request
@app.on_event("startup")
async def startup_event():
    print("Loading LLM Engine...")
    app.state.engine = PDFQueryEngine()
    print("LLM Engine loaded successfully.")

# Include routers
app.include_router(document_routes.router, prefix="/api")
app.include_router(query_routes.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
