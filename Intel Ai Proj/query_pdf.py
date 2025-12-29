"""
Question answering module using local LLM
"""
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from build_vectorstore import VectorStore

class PDFQueryEngine:
    def __init__(self, model_name="google/flan-t5-base"):
        """Initialize QA engine with local LLM"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            self.vector_store = VectorStore()
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def answer_question(self, question):
        """Answer question using retrieved context"""
        try:
            if not question.strip():
                return "Please provide a valid question."
            
            # Retrieve relevant chunks with scores
            relevant_chunks, scores = self.vector_store.search_with_score(question, n_results=3)
            
            # Debug: Print scores to help tune threshold
            if scores:
                print(f"DEBUG: Query '{question}' - Top Score: {scores[0]}")

            # Simple thresholding: L2 Distance. Lower is better.
            # 0.0 = exact match. > 1.4 is usually getting into "unrelated" territory for MiniLM.
            if not relevant_chunks or (scores and scores[0] > 1.4): 
                return "This content is not related to the PDF content provided."
            
            # Combine context
            context = "\n\n".join(relevant_chunks)
            
            # Create stricter prompt for T5 model
            prompt = (
                f"You are an intelligent assistant analyzing a document. "
                f"Answer the question below using ONLY the provided Context. "
                f"If the Context does not contain the answer, explicitly state: 'This content is not related to the PDF content provided'.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {question}\n\n"
                f"Answer:"
            )
            
            # Tokenize and generate
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
            
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=150,
                min_length=10,
                num_beams=4,
                length_penalty=1.0, # Reduce penalty to avoid forced length
                early_stopping=True,
                temperature=0.3 # Lower temperature for more factual answers
            )
            
            answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Post-processing to catch hallucination or partial failures
            if "not related" in answer.lower():
                return "This content is not related to the PDF content provided."
                
            return answer if answer.strip() else "Unable to generate answer."
        except Exception as e:
            print(f"Error answering question: {e}")
            return "Sorry, I encountered an error while processing your question."