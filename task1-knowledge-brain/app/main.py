"""FastAPI Server exposing Task 1 Knowledge Brain REST API."""
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import db
from app.schemas import (
    QueryRequest, QueryResponse,
    IngestionRunRequest, IngestionStatusResponse,
    EscalationRequest, EscalationRecord
)
from ingestion.crawler import crawler
from retrieval.rag import rag_service

app = FastAPI(
    title="Knowledge Brain API",
    description="Production REST API for Brilliant Directories Knowledge Base RAG service.",
    version=settings.app_version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Run initial sync on startup if database is empty
    stats = db.get_stats()
    if stats["total_articles"] == 0:
        print("[Startup] Database is empty. Running initial polite ingestion...")
        await crawler.run_sync(limit=10)

@app.get("/health")
def health():
    stats = db.get_stats()
    return {
        "status": "healthy",
        "service": settings.app_name,
        "articles_indexed": stats["active_articles"],
        "chunks_indexed": stats["total_chunks"]
    }

@app.post("/query", response_model=QueryResponse)
async def query_knowledge(req: QueryRequest):
    """Answers customer or system queries grounded in Brilliant Directories documentation."""
    try:
        response = await rag_service.answer_question(
            question=req.question,
            top_k=req.top_k,
            include_images=req.include_images,
            model_preference=req.model_preference
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingestion/run")
async def trigger_ingestion(req: IngestionRunRequest, bg: BackgroundTasks):
    """Triggers background incremental sitemap crawl."""
    if crawler.is_running:
        return {"status": "in_progress", "message": "An ingestion crawl is already active."}
    
    bg.add_task(crawler.run_sync, req.limit)
    return {"status": "started", "message": "Background ingestion crawl initiated."}

@app.get("/ingestion/status", response_model=IngestionStatusResponse)
def get_ingestion_status():
    stats = db.get_stats()
    return IngestionStatusResponse(
        is_running=crawler.is_running,
        total_articles=stats["total_articles"],
        active_articles=stats["active_articles"],
        total_chunks=stats["total_chunks"],
        total_images=stats["total_chunks"] * 1 # approximate ratio
    )

@app.post("/escalations/{escalation_id}/resolve")
def resolve_escalation(escalation_id: str, expert_answer: str, expert_name: str = "Senior Consultant"):
    """Resolves an escalation task and updates knowledge base."""
    db.resolve_escalation(escalation_id, expert_answer, expert_name)
    return {"status": "resolved", "escalation_id": escalation_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
