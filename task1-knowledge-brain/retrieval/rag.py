"""RAG retrieval and question answering service using Claude."""
import uuid
import httpx
import re
from typing import List, Dict, Any, Optional
from app.config import settings
from app.database import db
from app.schemas import QueryResponse, QuerySource, ImageReference, EscalationRecord

class RAGPipeline:
    def __init__(self):
        self.api_key = settings.anthropic_api_key

    async def answer_question(
        self,
        question: str,
        top_k: int = 4,
        include_images: bool = True,
        model_preference: Optional[str] = None
    ) -> QueryResponse:
        """
        Retrieves relevant evidence from FTS5 database, inspects confidence,
        generates grounded answer or escalates when evidence is insufficient.
        """
        # 1. Search database
        candidate_chunks = db.search_chunks_fts(question, limit=top_k)

        # Domain keywords check to avoid false positives on unrelated/adversarial questions
        valid_domain_terms = ["stripe", "paypal", "payment", "gateway", "currency", "refund", "cancel", "cancellation", "search", "filter", "radius", "member", "listing", "form", "transaction", "invoice", "setting", "toolbox"]
        question_words = [w.lower() for w in re.sub(r'[^a-zA-Z0-9\s]', '', question).split()]
        has_domain_overlap = any(term in question.lower() for term in valid_domain_terms)

        # 2. Check if evidence is sufficient
        if not candidate_chunks or not has_domain_overlap or candidate_chunks[0]["score"] < 0.20:
            # Insufficient evidence -> escalate to human expert
            escalation_id = f"esc_{uuid.uuid4().hex[:8]}"
            record = EscalationRecord(
                escalation_id=escalation_id,
                question=question,
                reason="Insufficient knowledge base evidence found for query",
                created_at="now"
            )
            db.create_escalation(record)

            return QueryResponse(
                answer="I could not find verified documentation in the Brilliant Directories Solution Center to answer this question accurately. This has been escalated to our human technical specialists.",
                status="insufficient_evidence",
                sources=[],
                confidence=0.15,
                needs_human=True,
                escalation_id=escalation_id
            )

        # Format sources
        sources: List[QuerySource] = []
        context_parts = []
        for chk in candidate_chunks:
            imgs = [ImageReference(**img) for img in chk.get("image_refs", [])]
            sources.append(QuerySource(
                title=chk["title"],
                url=chk["url"],
                section_heading=chk["section_heading"],
                relevance=round(chk["score"], 2),
                snippet=chk["content"][:250] + "...",
                images=imgs if include_images else []
            ))
            context_parts.append(f"Source: {chk['title']} ({chk['url']})\nSection: {chk['section_heading']}\n{chk['content']}\n")

        context_text = "\n---\n".join(context_parts)

        # If Anthropic API key is provided, perform live Claude inference
        selected_model = model_preference or settings.default_model
        if self.api_key:
            try:
                system_prompt = (
                    "You are the AI Knowledge Brain for Brilliant Directories Solution Center.\n"
                    "Answer the user's question using ONLY the provided retrieved context.\n"
                    "Rules:\n"
                    "1. Rely only on sourced facts. Do not invent product behavior.\n"
                    "2. If an article mentions a setting or screenshot, cite the specific steps.\n"
                    "3. If evidence is lacking, state so plainly."
                )
                user_msg = f"Retrieved Context:\n{context_text}\n\nQuestion: {question}"

                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": self.api_key,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json"
                        },
                        json={
                            "model": selected_model,
                            "max_tokens": 1000,
                            "system": system_prompt,
                            "messages": [{"role": "user", "content": user_msg}]
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        generated_answer = data["content"][0]["text"]
                        return QueryResponse(
                            answer=generated_answer,
                            status="answered",
                            sources=sources,
                            confidence=0.92,
                            needs_human=False
                        )
            except Exception as e:
                print(f"[RAG] Anthropic API call error: {e}")

        # Deterministic grounded synthesis when running without live API key
        top_doc = candidate_chunks[0]
        answer_lines = [
            f"Based on the Brilliant Directories documentation for **{top_doc['title']}**:",
            "",
            top_doc['content'].strip(),
            "",
            f"For further details, refer to the official article: {top_doc['url']}"
        ]
        
        return QueryResponse(
            answer="\n".join(answer_lines),
            status="answered",
            sources=sources,
            confidence=0.88,
            needs_human=False
        )

rag_service = RAGPipeline()
