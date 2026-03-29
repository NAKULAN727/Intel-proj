"""
Enterprise PDF Knowledge Base — Streamlit UI (Production Version)

Improvements over original:
- Uses new modular ingestion pipeline (semantic chunks + page metadata)
- Hybrid retrieval (BM25 + Dense + Reranker) via HybridRetriever
- Source attribution cards show page number + relevance score per chunk
- LLM auto-selects Phi-3 Mini (if available) or flan-t5-base (fallback)
- Table viewer loads from updated storage/tables_db.json
- Multi-column layout for cleaner UX
"""
import streamlit as st
import os
import time
from tinydb import TinyDB, Query
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Enterprise PDF Knowledge Base",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .source-card {
        background: #1e1e2e;
        border-left: 4px solid #7c6af7;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
    .source-meta {
        color: #a0a0b0;
        font-size: 0.8rem;
        margin-bottom: 6px;
    }
    .source-text {
        color: #d0d0e0;
        line-height: 1.5;
    }
    .badge {
        background: #7c6af7;
        color: white;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-green { background: #22c55e; }
    .badge-yellow { background: #eab308; color: #000; }
    .badge-red { background: #ef4444; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_file" not in st.session_state:
    st.session_state.current_file = None
if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0


# ── Helper Functions ──────────────────────────────────────────────────────────

def _show_tables():
    """Render extracted tables from TinyDB."""
    db_path = os.path.join("storage", "tables_db.json")
    if not os.path.exists(db_path):
        st.info("No tables database found. Build the knowledge base first.")
        return
    try:
        db = TinyDB(db_path)
        records = db.all()
        if not records:
            st.info("No tables found in this document.")
            return
        for rec in records:
            st.caption(f"📄 {rec.get('file', '?')} — Page {rec.get('page', '?')}")
            data = rec.get("data", [])
            if data and len(data) > 1:
                try:
                    df = pd.DataFrame(data[1:], columns=data[0])
                    st.dataframe(df, use_container_width=True)
                except Exception:
                    st.text(str(data))
            st.divider()
    except Exception as exc:
        st.error(f"Could not load tables: {exc}")


def _render_sources(sources: list):
    """Render source attribution cards below an answer."""
    with st.expander(f"📌 {len(sources)} source(s) used", expanded=False):
        for i, chunk in enumerate(sources):
            page     = chunk.get("page", "?")
            src      = chunk.get("source", "document")
            score    = chunk.get("rerank_score", chunk.get("score", 0.0))
            preview  = chunk.get("text", "")[:280].replace("\n", " ")

            # Colour-code relevance badge
            if score >= 5:
                badge_cls = "badge badge-green"
            elif score >= 0:
                badge_cls = "badge badge-yellow"
            else:
                badge_cls = "badge badge-red"

            st.markdown(
                f"""<div class="source-card">
  <div class="source-meta">
    <span class="{badge_cls}">Source {i+1}</span>
    &nbsp;📄 <b>{src}</b> &nbsp;·&nbsp; Page <b>{page}</b>
    &nbsp;·&nbsp; Relevance score: <code>{score:.3f}</code>
  </div>
  <div class="source-text">{preview}…</div>
</div>""",
                unsafe_allow_html=True
            )


def _run_ingestion(pdf_file):
    """Full ingestion pipeline: extract → chunk → index (vector + BM25)."""
    # Save PDF
    os.makedirs("storage", exist_ok=True)
    pdf_path = os.path.join("storage", "current.pdf")
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.getbuffer())

    with st.status("Processing PDF...", expanded=True) as status:
        try:
            # Step 1: Extract pages
            st.write("📄 Extracting text, tables, and images...")
            from ingestion.pdf_reader import extract_pages
            pages = extract_pages(pdf_path)
            st.write(f"✅ {len(pages)} pages extracted")

            if not pages or all(len(p["text"].strip()) == 0 for p in pages):
                st.error("❌ No text extracted. Is this a scanned PDF without OCR support?")
                return

            # Step 2: Semantic chunking
            st.write("✂️ Chunking into semantic units...")
            from ingestion.chunker import semantic_chunk
            chunks = semantic_chunk(pages)
            st.write(f"✅ {len(chunks)} chunks created")

            if not chunks:
                st.error("Chunking produced no results. Check the PDF content.")
                return

            # Step 3: Build ChromaDB vector index
            st.write("🧠 Building vector index (ChromaDB)...")
            from retrieval.vector_store import VectorStore
            vs = VectorStore()
            vs.clear()
            vs.add_documents(chunks)
            st.write(f"✅ {len(chunks)} chunks indexed in ChromaDB")

            # Step 4: Build BM25 keyword index
            st.write("🔑 Building BM25 keyword index...")
            from retrieval.bm25_store import BM25Store
            bm25 = BM25Store()
            bm25.build(chunks)
            st.write("✅ BM25 index built")

            # Update session state
            st.session_state.current_file = pdf_file.name
            st.session_state.chunk_count = len(chunks)
            st.session_state.messages = []   # clear chat history for new doc

            # Reload the QA engine with fresh indexes
            st.cache_resource.clear()

            status.update(label="✅ Knowledge base ready!", state="complete")
            time.sleep(1)
            st.rerun()

        except Exception as exc:
            st.error(f"❌ Build failed: {exc}")
            import traceback
            st.code(traceback.format_exc())


@st.cache_resource(show_spinner="Loading AI engine...")
def load_engine():
    from generation.llm_engine import PDFQueryEngine
    return PDFQueryEngine()



# ── Header ────────────────────────────────────────────────────────────────────
st.title("📚 Enterprise PDF Knowledge Base")
st.markdown("**Hybrid search · Source attribution · Local AI — no API keys needed**")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Setup")

    with st.expander("ℹ️ How It Works"):
        st.markdown("""
**Ingestion**
- Text extracted with `pdfplumber` (OCR fallback via Tesseract)
- Tables converted to searchable text and stored in TinyDB
- Images captioned by Salesforce BLIP at 150 DPI
- Text split into semantic chunks (sentence-boundary aware)

**Retrieval (Hybrid)**
- BM25 keyword search → catches exact terms
- Dense vector search (MiniLM) → catches semantic meaning
- Cross-encoder reranker → best chunk surfaces to top

**Generation**
- Phi-3 Mini GGUF (primary) — 4096 token context
- flan-t5-base (fallback) — auto-selected if model not found
        """)

    st.divider()

    # ── File uploader ─────────────────────────────────────────────────────────
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

    if pdf_file:
        if st.session_state.current_file != pdf_file.name:
            st.warning("⚠️ New file detected. Click 'Build Knowledge Base' to index it.")
        else:
            st.success(f"✅ Indexed: **{pdf_file.name}**  ({st.session_state.chunk_count} chunks)")

        if st.button("🔨 Build / Reset Knowledge Base", use_container_width=True):
            _run_ingestion(pdf_file)
    else:
        st.info("Upload a PDF to begin.")

    st.divider()

    # ── Table viewer ──────────────────────────────────────────────────────────
    st.markdown("### 📊 Extracted Tables")
    if st.checkbox("Show tables from document"):
        _show_tables()

    st.divider()
    st.caption("All processing runs locally. No data leaves your machine.")


# ── Ingestion pipeline (called after upload) ──────────────────────────────────






# ── QA Engine (cached across reruns) ─────────────────────────────────────────



try:
    engine = load_engine()
except Exception as exc:
    st.error(f"❌ Failed to load AI engine: {exc}")
    st.info("Make sure all dependencies are installed: `pip install -r requirements.txt`")
    st.stop()


# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
            _render_sources(msg["sources"])





# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask anything about your document..."):
    # Guard: make sure a document is indexed
    if st.session_state.current_file is None:
        st.warning("⚠️ Please upload and build a knowledge base first.")
        st.stop()

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, sources = engine.answer_question(prompt)

        st.markdown(answer)
        if sources:
            _render_sources(sources)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })
