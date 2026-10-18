"""Pydantic data schemas for Task 1: Knowledge Brain."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ImageReference(BaseModel):
    image_url: str
    caption: Optional[str] = None
    surrounding_text: Optional[str] = None
    ai_description: Optional[str] = None
    ui_elements: List[str] = Field(default_factory=list)

class ArticleChunk(BaseModel):
    chunk_id: str
    article_id: str
    title: str
    url: str
    section_heading: str
    content: str
    image_refs: List[ImageReference] = Field(default_factory=list)

class ArticleDocument(BaseModel):
    article_id: str
    title: str
    url: str
    category: Optional[str] = None
    folder: Optional[str] = None
    last_modified: Optional[str] = None
    content_hash: str
    raw_html: Optional[str] = None
    cleaned_text: str
    headings: List[str] = Field(default_factory=list)
    images: List[ImageReference] = Field(default_factory=list)
    chunks: List[ArticleChunk] = Field(default_factory=list)
    status: str = "active" # active, updated, removed

class QuerySource(BaseModel):
    title: str
    url: str
    section_heading: Optional[str] = None
    relevance: float = Field(ge=0.0, le=1.0)
    snippet: Optional[str] = None
    images: List[ImageReference] = Field(default_factory=list)

class QueryRequest(BaseModel):
    question: str
    top_k: int = 4
    include_images: bool = True
    model_preference: Optional[str] = None # 'claude-3-5-sonnet', 'claude-3-5-haiku'

class QueryResponse(BaseModel):
    answer: str
    status: str = "answered" # "answered", "insufficient_evidence", "escalated"
    sources: List[QuerySource] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    needs_human: bool = False
    escalation_id: Optional[str] = None

class EscalationRequest(BaseModel):
    question: str
    reason: str
    context: Optional[Dict[str, Any]] = None

class EscalationRecord(BaseModel):
    escalation_id: str
    question: str
    reason: str
    status: str = "pending" # pending, resolved
    created_at: str
    resolved_at: Optional[str] = None
    expert_answer: Optional[str] = None
    expert_name: Optional[str] = None

class IngestionRunRequest(BaseModel):
    limit: Optional[int] = None
    force_refresh: bool = False

class IngestionStatusResponse(BaseModel):
    is_running: bool
    total_articles: int
    active_articles: int
    total_chunks: int
    total_images: int
    last_sync_timestamp: Optional[str] = None
    added_last_run: int = 0
    updated_last_run: int = 0
    removed_last_run: int = 0
    failed_last_run: int = 0
