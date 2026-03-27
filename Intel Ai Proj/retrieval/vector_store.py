"""
ChromaDB vector store with page/source metadata support.

Key improvement over original:
- Stores page number and source filename per chunk
- Returns metadata alongside text in search results
- Enables source attribution in the UI
"""
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict


class VectorStore:
    def __init__(
        self,
        collection_name: str = "pdf_knowledge",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        db_path: str = "./chroma_db"
    ):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer(model_name)
        self._get_or_create_collection()

    def _get_or_create_collection(self):
        try:
            self.collection = self.client.get_collection(self.collection_name)
        except Exception:
            self.collection = self.client.create_collection(self.collection_name)

    def add_documents(self, chunks: List[Dict]):
        """
        Add chunks with metadata to the vector store.

        Args:
            chunks: List of {"text": str, "page": int, "chunk_index": int, "source": str}
        """
        if not chunks:
            return

        texts = [c["text"] for c in chunks]
        print(f"Encoding {len(texts)} chunks...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        ids = [f"chunk_{c['chunk_index']}" for c in chunks]
        metadatas = [
            {
                "page": int(c["page"]),
                "source": str(c["source"]),
                "chunk_index": int(c["chunk_index"])
            }
            for c in chunks
        ]

        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        print(f"ChromaDB: {len(chunks)} chunks indexed.")

    def search(self, query: str, n_results: int = 6) -> List[Dict]:
        """
        Search for relevant chunks.

        Returns:
            List of {"text": str, "page": int, "source": str, "score": float}
        """
        query_emb = self.embedding_model.encode([query])
        results = self.collection.query(
            query_embeddings=query_emb.tolist(),
            n_results=min(n_results, self.collection.count()),
            include=["documents", "distances", "metadatas"]
        )

        output = []
        for doc, dist, meta in zip(
            results["documents"][0],
            results["distances"][0],
            results["metadatas"][0]
        ):
            output.append({
                "text": doc,
                "page": meta.get("page", "?"),
                "source": meta.get("source", "?"),
                "score": round(1 - dist, 4)  # convert L2 distance to similarity
            })
        return output

    def count(self) -> int:
        """Return total number of indexed chunks."""
        return self.collection.count()

    def clear(self):
        """Delete and recreate the collection."""
        self.client.delete_collection(self.collection_name)
        self._get_or_create_collection()
        print("ChromaDB collection cleared.")
