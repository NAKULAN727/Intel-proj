"""
BM25 keyword-based retrieval index.

Why BM25 alongside dense vectors?
- BM25 excels at exact keyword matches (names, codes, numbers)
- Dense vectors excel at semantic/paraphrase matches
- Together: ~30-50% better retrieval coverage

Requires: pip install rank-bm25
"""
from rank_bm25 import BM25Okapi
from typing import List, Dict
import pickle
import os
import re


class BM25Store:
    def __init__(self, index_path: str = "bm25_index.pkl"):
        self.index_path = index_path
        self.corpus: List[Dict] = []
        self.bm25: BM25Okapi = None

    def build(self, chunks: List[Dict]):
        """
        Build BM25 index from chunk dicts.

        Args:
            chunks: List of {"text": str, "page": int, "source": str, ...}
        """
        self.corpus = chunks
        tokenized = [self._tokenize(c["text"]) for c in chunks]
        self.bm25 = BM25Okapi(tokenized)

        with open(self.index_path, "wb") as f:
            pickle.dump((self.corpus, self.bm25), f)
        print(f"BM25 index built: {len(chunks)} documents.")

    def load(self) -> bool:
        """Load index from disk. Returns True if successful."""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "rb") as f:
                    self.corpus, self.bm25 = pickle.load(f)
                print(f"BM25 index loaded: {len(self.corpus)} documents.")
                return True
            except Exception as e:
                print(f"BM25 index load failed: {e}")
        return False

    def search(self, query: str, n_results: int = 6) -> List[Dict]:
        """
        Return top-n chunks by BM25 score.

        Args:
            query: Search query string
            n_results: Number of results to return

        Returns:
            List of chunk dicts (same format as input to build())
        """
        if not self.bm25 or not self.corpus:
            return []

        tokens = self._tokenize(query)
        scores = self.bm25.get_scores(tokens)

        # Get top indices with positive scores only
        top_idx = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:n_results]

        results = []
        for i in top_idx:
            if scores[i] > 0:
                chunk = dict(self.corpus[i])  # copy to avoid mutation
                chunk["bm25_score"] = float(scores[i])
                results.append(chunk)

        return results

    def clear(self):
        """Remove index from disk."""
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        self.corpus = []
        self.bm25 = None

    def _tokenize(self, text: str) -> List[str]:
        """Simple whitespace + punctuation tokenizer."""
        return re.findall(r'\b\w+\b', text.lower())
