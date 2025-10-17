"""
Main entry point for PDF Knowledge Base system
"""
import os
from pdf_reader import extract_text_from_pdf, chunk_text
from build_vectorstore import VectorStore
from query_pdf import PDFQueryEngine

def main():
    """Main function to run the PDF knowledge base system"""
    pdf_path = "sample.pdf"
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found. Please place your PDF file in the current directory.")
        return
    
    print("🔄 Building knowledge base from PDF...")
    
    try:
        # Step 1: Extract text from PDF
        print("📄 Extracting text from PDF...")
        text = extract_text_from_pdf(pdf_path)
        
        if not text.strip():
            print("Error: No text found in PDF. Make sure the PDF contains readable text.")
            return
        
        print(f"✅ Extracted {len(text)} characters from PDF")
        
        # Step 2: Split into chunks
        print("✂️ Splitting text into chunks...")
        chunks = chunk_text(text)
        print(f"✅ Created {len(chunks)} text chunks")
        
        # Step 3: Build vector database
        print("🧠 Building vector database...")
        vector_store = VectorStore()
        vector_store.add_documents(chunks)
        print("✅ Vector database created successfully")
        
        # Step 4: Initialize QA engine
        print("🤖 Loading AI model...")
        qa_engine = PDFQueryEngine()
        print("✅ AI model loaded successfully")
    except Exception as e:
        print(f"Error during setup: {e}")
        return
    
    # Step 5: Interactive Q&A loop
    print("\n" + "="*50)
    print("🎯 PDF Knowledge Base Ready!")
    print("="*50)
    
    while True:
        question = input("\n❓ Ask a question about the PDF (or 'quit' to exit): ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not question:
            continue
        
        print("\n🔍 Searching for relevant information...")
        answer = qa_engine.answer_question(question)
        
        print(f"\n💡 Answer: {answer}")
        print("-" * 50)

if __name__ == "__main__":
    main()