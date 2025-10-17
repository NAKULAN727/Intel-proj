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
            
            # Retrieve relevant chunks
            relevant_chunks = self.vector_store.search(question, n_results=3)
            
            if not relevant_chunks:
                return "No relevant information found in the PDF."
            
            # Combine context
            context = "\n\n".join(relevant_chunks)
            
            # Create prompt for T5 model
            prompt = f"Answer the question based on the context.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"
            
            # Tokenize and generate
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=150,
                num_beams=4,
                early_stopping=True,
                temperature=0.7
            )
            
            answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return answer if answer.strip() else "Unable to generate answer."
        except Exception as e:
            print(f"Error answering question: {e}")
            return "Sorry, I encountered an error while processing your question."