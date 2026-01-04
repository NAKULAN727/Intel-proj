import streamlit as st
import os
import time
from pdf_reader import extract_text_and_tables, chunk_text
from build_vectorstore import VectorStore
from query_pdf import PDFQueryEngine
from tinydb import TinyDB
import pandas as pd

# Set page config
st.set_page_config(page_title="Enterprise PDF Knowledge Base", layout="wide")

st.title("📚 PDF Knowledge Base with AI")
st.markdown("Search inside your documents (Text, Tables, and Images)")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for Setup
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/87/PDF_file_icon.svg", width=50) 
    st.header("Settings")
    
    with st.expander("ℹ️ How it Works"):
        st.markdown("""
        **1. Ingestion**: 
        - Reads text using `pdfplumber`.
        - Scanned pages? Auto-switches to `Tesseract OCR`.
        - Images? Captioned by `Salesforce BLIP`.
        
        **2. Indexing**:
        - Text is split into chunks (1000 chars).
        - Converted to numbers (vectors) using `MiniLM-L6`.
        - Stored in `ChromaDB`. Tables go to `TinyDB`.
        
        **3. Retrieval (RAG)**:
        - Your question is converted to a vector.
        - We find the top 5 most similar chunks.
        - `Flan-T5` (a local AI) reads them and answers you.
        """)
    
    pdf_file = st.file_uploader("Upload PDF", type=['pdf'])
    
    # Check if a file is uploaded
    if pdf_file:
        # Check if this specific file has been processed
        if "current_file" not in st.session_state or st.session_state.current_file != pdf_file.name:
            st.warning("⚠️ File uploaded but not indexed yet. Click 'Build Knowledge Base'.")
        else:
            st.success(f"✅ Indexing Active: {pdf_file.name}")

        if st.button("Build/Reset Knowledge Base"):
            # Save uploaded file
            with open("sample.pdf", "wb") as f:
                f.write(pdf_file.getbuffer())
            
            with st.status("Processing PDF..."):
                st.write("📄 Extracting text, tables, and images...")
                # Extract
                text = extract_text_and_tables("sample.pdf")
                
                if len(text.strip()) == 0:
                    st.error("❌ No text extracted! Is this a scanned PDF without OCR?")
                    st.stop()
                
                st.write(f"✅ Extracted {len(text)} characters")
                
                # Chunk
                st.write("✂️ Splitting into chunks...")
                chunks = chunk_text(text)
                st.write(f"✅ Created {len(chunks)} chunks")
                
                if len(chunks) == 0:
                    st.error("Text was extracted but no chunks created. Check chunking logic.")
                    st.stop()

                # Build Vector DB
                st.write("🧠 Building Vector Store...")
                try:
                    vs = VectorStore()
                    vs.clear() # Clear old data
                    vs.add_documents(chunks)
                    st.session_state.current_file = pdf_file.name
                    st.success("Knowledge Base Ready!")
                    
                    # Clear the cached engine so it reloads with new data
                    st.cache_resource.clear()
                    
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to build vector store: {e}")
        
    else:
        st.info("Please upload a PDF to start.")

    st.divider()
    st.markdown("### Extracted Artifacts")
    if st.checkbox("Show Extracted Tables"):
        try:
            db = TinyDB('tables_db.json')
            tables = db.all()
            if tables:
                for idx, tbl in enumerate(tables):
                    st.caption(f"Table from Page {tbl['page']}")
                    # Convert list of lists to dataframe
                    if tbl['data']:
                        df = pd.DataFrame(tbl['data'][1:], columns=tbl['data'][0])
                        st.dataframe(df)
                    st.divider()
            else:
                st.info("No tables found in database.")
        except Exception as e:
            st.error(f"Could not load tables: {e}")

# Main Chat Interface
@st.cache_resource
def load_qa_engine():
    return PDFQueryEngine()

try:
    engine = load_qa_engine()
except Exception as e:
    st.error(f"Model loading failed: {e}")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about your document..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response, context_chunks = engine.answer_question(prompt)
            st.markdown(response)
            
            # Debug: Show retrieved context
            with st.expander("🔍 Debug: What did the AI read?"):
                try:
                    if context_chunks:
                        for i, chunk in enumerate(context_chunks):
                            st.markdown(f"**Chunk {i+1}:**")
                            st.text(chunk[:300] + "...") # Preview
                    else:
                        st.warning("No context retrieved.")
                except Exception as e:
                    st.text(f"Could not display debug context: {e}")
    
    # Add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
