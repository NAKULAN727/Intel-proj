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
                return "Please provide a valid question.", []
            
            # Retrieve relevant chunks with scores
            relevant_chunks, scores = self.vector_store.search_with_score(question, n_results=3)
            
            # Debug: Print scores
            if scores:
                print(f"DEBUG: Query '{question}' - Top Score: {scores[0]}")
            
            # Special handling for Summarization
            # If the user asks for a summary, vector search often fails because "summary" isn't in the text.
            # We explicitly inject the first few chunks (Introduction) which usually contain the summary/abstract/authors.
            summary_keywords = ["summarize", "summary", "about", "overview", "explain", "what is this", "author", "who wrote", "who is", "message", "theme", "moral"]
            if any(keyword in question.lower() for keyword in summary_keywords):
                try:
                    print("DEBUG: Summary intent detected. Fetching first chunks.")
                    first_chunk = self.vector_store.get_by_id("chunk_0")
                    second_chunk = self.vector_store.get_by_id("chunk_1")
                    
                    # Prepend first chunks to context if they exist and aren't already there
                    if second_chunk and second_chunk not in relevant_chunks:
                        relevant_chunks.insert(0, second_chunk)
                    if first_chunk and first_chunk not in relevant_chunks:
                        relevant_chunks.insert(0, first_chunk)
                except Exception as sum_e:
                    print(f"Error fetching summary chunks: {sum_e}")
                    # Continue without summary chunks

            # Special handling for "What can I ask?" / Help
            help_keywords = ["what can i ask", "what questions", "how to use", "guide me", "capabilities"]
            if any(question.lower().strip() == k or (k in question.lower() and len(k) > 5) for k in help_keywords):
                help_response = (
                    "You can ask me regarding:\n"
                    "1. **Summaries**: 'Summarize the document', 'What is this about?'\n"
                    "2. **Specific Details**: Ask about dates, names, figures, or specific sections defined in the PDF.\n"
                    "3. **Tables & Images**: I can search through extracted tables and image captions.\n"
                    "4. **General Chat**: 'Hi', 'How are you?'"
                )
                return help_response, []

            # Combine context
            if relevant_chunks:
                context = "\n\n".join(relevant_chunks)
            else:
                context = "No specific context available."
            
            # Create flexible prompt for T5 model
            # Tailor instructions based on query type to help the model focus
            valid_instruction = "Use the provided Context to answer the Question in detail."
            
            if any(k in question.lower() for k in ["author", "who wrote", "created by"]):
                valid_instruction = "Extract the names of the people listed as authors of the document. Ignore conference names, publishers, or dates."
            elif any(k in question.lower() for k in ["summary", "summarize", "about", "overview", "what is this", "explain", "message", "theme", "moral"]):
                valid_instruction = "Summarize the main topic and key points of the document based on the provided Context. Do not pick a single random sentence."

            prompt = (
                f"You are a helpful AI assistant. {valid_instruction} "
                f"If the Question is general conversation (e.g. greetings, general questions), answer politely. "
                f"If the answer is not in the context and it's not a general question, say 'I couldn't find that in the document'.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {question}\n\n"
                f"Answer:"
            )
            
            # Tokenize and generate
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
            
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=200,
                min_length=2, # Allow shorter answers like "Hi"
                num_beams=4,
                length_penalty=1.0,
                repetition_penalty=1.2, # Prevent repeating the same phrases
                early_stopping=True,
                temperature=0.5 # Lower temperature for more focused answers
            )
            
            answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Post-processing
            # if "not related" in answer.lower():
            #     return "This content is not related to the PDF content provided.", relevant_chunks
                
            final_answer = answer if answer.strip() else "Unable to generate answer."
            return final_answer, relevant_chunks
        except Exception as e:
            print(f"Error answering question: {e}")
            return f"Error: {str(e)}", []