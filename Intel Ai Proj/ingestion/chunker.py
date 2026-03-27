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
    chunk_size: int = 5,   # number of sentences per chunk
    overlap: int = 1       # sentence overlap between consecutive chunks
) -> List[Dict]:
    """
    Chunk text by sentences while preserving page-level metadata.

    Args:
        pages: List of {"page": int, "text": str, "source": str}
        chunk_size: How many sentences per chunk
        overlap: How many sentences from previous chunk to include

    Returns:
        List of {"text": str, "page": int, "chunk_index": int, "source": str}
    """
    all_chunks = []
    chunk_index = 0

    for page_info in pages:
        page_num = page_info["page"]
        source = page_info.get("source", "unknown.pdf")
        sentences = split_into_sentences(page_info["text"])

        if not sentences:
            continue

        i = 0
        while i < len(sentences):
            window = sentences[i: i + chunk_size]
            chunk_text = " ".join(window)

            if len(chunk_text.strip()) > 30:  # skip near-empty chunks
                all_chunks.append({
                    "text": chunk_text,
                    "page": page_num,
                    "chunk_index": chunk_index,
                    "source": source,
                })
                chunk_index += 1

            i += max(1, chunk_size - overlap)

    return all_chunks
