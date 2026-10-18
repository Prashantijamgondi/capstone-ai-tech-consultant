"""Document chunking strategies."""
import re
from typing import List
from app.schemas import ArticleChunk, ImageReference

class DocumentChunker:
    def __init__(self, target_chunk_size: int = 500, overlap: int = 50):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap

    def chunk_article(
        self,
        article_id: str,
        title: str,
        url: str,
        cleaned_text: str,
        headings: List[str],
        images: List[ImageReference]
    ) -> List[ArticleChunk]:
        """
        Splits text into chunks preserving sections, headings, instructions and keeping nearby images attached.
        """
        # Split on section headings or double newlines
        sections = re.split(r'\n(?=#{1,4}\s+|[A-Z0-9\s]{3,30}:\n)', cleaned_text)
        chunks: List[ArticleChunk] = []

        chunk_counter = 1
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue

            # Extract heading if present
            lines = sec.split("\n")
            first_line = lines[0].replace("#", "").strip()
            section_heading = first_line if len(first_line) < 80 else "General Information"
            
            # Associate any images mentioned or relevant
            sec_images = [img for img in images if img.image_url in sec or any(ui.lower() in sec.lower() for ui in img.ui_elements)]
            if not sec_images and images:
                # Include first image as default reference if none explicitly matched
                sec_images = [images[0]]

            chunk_id = f"{article_id}_chk_{chunk_counter:03d}"
            chunks.append(ArticleChunk(
                chunk_id=chunk_id,
                article_id=article_id,
                title=title,
                url=url,
                section_heading=section_heading,
                content=sec,
                image_refs=sec_images
            ))
            chunk_counter += 1

        # Fallback if no sections were parsed
        if not chunks:
            chunks.append(ArticleChunk(
                chunk_id=f"{article_id}_chk_001",
                article_id=article_id,
                title=title,
                url=url,
                section_heading=title,
                content=cleaned_text[:1000],
                image_refs=images
            ))

        return chunks

chunker = DocumentChunker()
