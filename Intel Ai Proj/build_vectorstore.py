"""
Vector database creation using ChromaDB and sentence transformers
"""
import chromadb
from sentence_transformers import SentenceTransformer
import os

class VectorStore:
    def __init__(self, collection_name="pdf_knowledge", model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize vector store with embedding model"""
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer(model_name)
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception as e:
            print(f"Collection not found, creating new one: {e}")
            self.collection = self.client.create_collection(collection_name)
    
    def add_documents(self, texts):
        """Add text chunks to vector database"""
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Create IDs and metadata
        ids = [f"chunk_{i}" for i in range(len(texts))]
        metadatas = [{"text": text} for text in texts]
        
        # Add to collection
        try:
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added {len(texts)} chunks to vector database")
        except Exception as e:
            print(f"Error adding documents: {e}")
            raise
    
    def clear(self):
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(self.collection_name)
            print("✅ Collection cleared successfully")
        except Exception as e:
            print(f"Error clearing collection: {e}")

    
    def search_with_score(self, query, n_results=3):
        """Search and return docs with their distances"""
        try:
            query_embedding = self.embedding_model.encode([query])
            
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                include=['documents', 'distances']
            )
            
            return results['documents'][0], results['distances'][0]
        except Exception as e:
            print(f"Error searching: {e}")
            return [], []

    def search(self, query, n_results=3):
        """Wrapper for backward compatibility"""
        docs, _ = self.search_with_score(query, n_results)
        return docs

    def get_by_id(self, doc_id):
        """Retrieve a specific document by its ID"""
        try:
            result = self.collection.get(ids=[doc_id])
            if result and result['documents']:
                return result['documents'][0]
            return None
        except Exception as e:
            print(f"Error getting document by ID: {e}")
            return None