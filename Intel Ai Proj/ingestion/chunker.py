"""
Semantic chunker: splits text on sentence boundaries, preserves page metadata.
No external NLP libraries needed — pure regex.
"""
from typing import List, Dict
import re


def split_into_sentences(text: str) -> List[str]:
    """Split a block of text into sentences using regex."""
    # Split on period/!/? followed by space + capital letter
    pattern = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
    sentences = pattern.split(text)
    return [s.strip() for s in sentences if s.strip()]


def semantic_chunk(
    pages: List[Dict],
    max_words: int = 250,
    overlap_words: int = 40
) -> List[Dict]:
    """
    Chunk text using a sliding window word-based approach.
    Normalizes text by replacing newlines with spaces and removing excessive whitespace.
    """
    all_chunks = []
    chunk_index = 0

    for page_info in pages:
        page_num = page_info["page"]
        source = page_info.get("source", "unknown.pdf")
        
        # Preprocessing: Normalize text
        text = page_info.get("text", "")
        text = text.replace("\n", " ")
        text = re.sub(r'\s+', ' ', text).strip()
        
        words = text.split()
        
        if not words:
            continue

        for i in range(0, len(words), max_words - overlap_words):
            chunk_words = words[i:i + max_words]
            chunk_text = " ".join(chunk_words)
            
            # Avoid very small chunks (<50 words) unless it's the only chunk for a short doc
            if len(chunk_words) >= 50 or (len(words) < 50 and i == 0):
                all_chunks.append({
                    "text": chunk_text,
                    "page": page_num,
                    "chunk_index": chunk_index,
                    "source": source,
                })
                chunk_index += 1

    print(f"✅ Chunking Complete: Generated {len(all_chunks)} total chunks.")
    return all_chunks
