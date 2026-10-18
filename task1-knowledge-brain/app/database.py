"""Storage and database operations for Knowledge Brain."""
import sqlite3
import json
import os
import re
from typing import List, Optional, Dict, Any
from app.config import settings
from app.schemas import ArticleDocument, ArticleChunk, EscalationRecord

class Database:
    def __init__(self, db_path: str = settings.database_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Articles table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                article_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                category TEXT,
                folder TEXT,
                last_modified TEXT,
                content_hash TEXT NOT NULL,
                cleaned_text TEXT NOT NULL,
                headings_json TEXT,
                images_json TEXT,
                status TEXT DEFAULT 'active',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Chunks table for keyword and semantic search
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                article_id TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                section_heading TEXT,
                content TEXT NOT NULL,
                image_refs_json TEXT,
                FOREIGN KEY (article_id) REFERENCES articles(article_id) ON DELETE CASCADE
            );
            """)

            # Full Text Search virtual table for chunks
            cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                chunk_id UNINDEXED,
                title,
                section_heading,
                content,
                tokenize = 'porter unicode61'
            );
            """)

            # Human Escalation Tasks table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS escalations (
                escalation_id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                expert_answer TEXT,
                expert_name TEXT
            );
            """)

            # Sync and ingestion history
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                added INTEGER DEFAULT 0,
                updated INTEGER DEFAULT 0,
                removed INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                status TEXT DEFAULT 'completed'
            );
            """)
            conn.commit()

    def save_article(self, article: ArticleDocument):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO articles (
                article_id, title, url, category, folder, last_modified,
                content_hash, cleaned_text, headings_json, images_json, status, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(article_id) DO UPDATE SET
                title=excluded.title,
                url=excluded.url,
                category=excluded.category,
                folder=excluded.folder,
                last_modified=excluded.last_modified,
                content_hash=excluded.content_hash,
                cleaned_text=excluded.cleaned_text,
                headings_json=excluded.headings_json,
                images_json=excluded.images_json,
                status=excluded.status,
                updated_at=CURRENT_TIMESTAMP;
            """, (
                article.article_id,
                article.title,
                article.url,
                article.category,
                article.folder,
                article.last_modified,
                article.content_hash,
                article.cleaned_text,
                json.dumps(article.headings),
                json.dumps([img.model_dump() for img in article.images]),
                article.status
            ))

            # Delete old chunks for this article
            cursor.execute("DELETE FROM chunks WHERE article_id = ?", (article.article_id,))
            cursor.execute("DELETE FROM chunks_fts WHERE chunk_id IN (SELECT chunk_id FROM chunks WHERE article_id = ?)", (article.article_id,))

            # Insert new chunks
            for chk in article.chunks:
                cursor.execute("""
                INSERT INTO chunks (chunk_id, article_id, title, url, section_heading, content, image_refs_json)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    chk.chunk_id,
                    chk.article_id,
                    chk.title,
                    chk.url,
                    chk.section_heading,
                    chk.content,
                    json.dumps([img.model_dump() for img in chk.image_refs])
                ))
                cursor.execute("""
                INSERT INTO chunks_fts (chunk_id, title, section_heading, content)
                VALUES (?, ?, ?, ?);
                """, (
                    chk.chunk_id,
                    chk.title,
                    chk.section_heading,
                    chk.content
                ))
            conn.commit()

    def deactivate_article(self, article_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE articles SET status = 'removed' WHERE article_id = ?", (article_id,))
            cursor.execute("DELETE FROM chunks WHERE article_id = ?", (article_id,))
            cursor.execute("DELETE FROM chunks_fts WHERE chunk_id NOT IN (SELECT chunk_id FROM chunks)")
            conn.commit()

    def search_chunks_fts(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            clean_terms = [re.sub(r'[^a-zA-Z0-9]', '', w) for w in query.split()]
            clean_terms = [w for w in clean_terms if len(w) > 2]
            if not clean_terms:
                return []

            # Match any relevant terms
            fts_query = " OR ".join([f'"{term}"*' for term in clean_terms])

            sql = """
            SELECT c.chunk_id, c.article_id, c.title, c.url, c.section_heading, c.content, c.image_refs_json,
                   bm25(chunks_fts) as rank
            FROM chunks_fts
            JOIN chunks c ON chunks_fts.chunk_id = c.chunk_id
            JOIN articles a ON c.article_id = a.article_id
            WHERE chunks_fts MATCH ? AND a.status = 'active'
            ORDER BY rank
            LIMIT ?;
            """
            try:
                cursor.execute(sql, (fts_query, limit))
                rows = cursor.fetchall()
                if not rows:
                    return []
                results = []
                for r in rows:
                    raw_rank = float(r["rank"])
                    score = min(0.99, max(0.1, 1.0 / (1.0 + abs(raw_rank))))
                    results.append({
                        "chunk_id": r["chunk_id"],
                        "article_id": r["article_id"],
                        "title": r["title"],
                        "url": r["url"],
                        "section_heading": r["section_heading"],
                        "content": r["content"],
                        "image_refs": json.loads(r["image_refs_json"]) if r["image_refs_json"] else [],
                        "score": score
                    })
                return results
            except Exception:
                return []

    def create_escalation(self, escalation: EscalationRecord):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO escalations (escalation_id, question, reason, status, created_at)
            VALUES (?, ?, ?, ?, ?);
            """, (
                escalation.escalation_id,
                escalation.question,
                escalation.reason,
                escalation.status,
                escalation.created_at
            ))
            conn.commit()

    def resolve_escalation(self, escalation_id: str, answer: str, expert_name: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE escalations
            SET status = 'resolved', expert_answer = ?, expert_name = ?, resolved_at = CURRENT_TIMESTAMP
            WHERE escalation_id = ?;
            """, (answer, expert_name, escalation_id))
            conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM articles")
            total_articles = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM articles WHERE status = 'active'")
            active_articles = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM chunks")
            total_chunks = cursor.fetchone()[0]
            return {
                "total_articles": total_articles,
                "active_articles": active_articles,
                "total_chunks": total_chunks
            }

db = Database()
