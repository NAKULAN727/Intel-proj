"""
LLM Engine: Local QA using Phi-3 Mini GGUF (primary) or flan-t5-base (fallback).

PRIMARY  : Phi-3 Mini 4K Instruct Q4_K_M via llama-cpp-python
  - 3.8B params, ~2.4 GB RAM, runs on any laptop CPU
  - 4096 token context, strong instruction following
  - Download: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
    File    : Phi-3-mini-4k-instruct-q4.gguf
    Save to : models/phi3-mini-q4.gguf

FALLBACK : google/flan-t5-base  (auto-selected when GGUF file is missing)

Install llama-cpp-python (CPU-only build):
    pip install llama-cpp-python
"""
import os
from typing import Tuple, List, Dict
from retrieval.hybrid_retriever import HybridRetriever

MODEL_PATH = os.path.join("models", "phi3-mini-q4.gguf")

# ---------------------------------------------------------------------------
# Phi-3 ChatML tokens built at runtime so editors / linters don't choke on them
# _tok("system") -> <|system|>   _tok("end") -> <|end|>   etc.
# ---------------------------------------------------------------------------
def _tok(name: str) -> str:
    pipe = chr(124)   # |
    lt   = chr(60)    # <
    gt   = chr(62)    # >
    return f"{lt}{pipe}{name}{pipe}{gt}"

_SYS_OPEN  = _tok("system")
_SYS_END   = _tok("end")
_USR_OPEN  = _tok("user")
_ASST_OPEN = _tok("assistant")


class PDFQueryEngine:
    """
    Orchestrates retrieval + generation for document QA.
    Automatically picks the best available local LLM.
    """

    def __init__(self):
        self.retriever = HybridRetriever()
        self.use_phi3 = False
        self._load_llm()

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------

    def _load_llm(self):
        """Load Phi-3 Mini if the GGUF file exists, otherwise fall back."""
        if os.path.exists(MODEL_PATH):
            self._load_phi3()
        else:
            print(f"[LLM] Phi-3 model not found at: {MODEL_PATH}")
            print("[LLM] To upgrade: download Phi-3-mini-4k-instruct-q4.gguf "
                  "from HuggingFace and place it in models/")
            print("[LLM] Falling back to flan-t5-base ...")
            self._load_t5()

    def _load_phi3(self):
        """Load Phi-3 Mini via llama-cpp-python."""
        try:
            from llama_cpp import Llama
            print("[LLM] Loading Phi-3 Mini (~8 seconds) ...")
            self.llm = Llama(
                model_path=MODEL_PATH,
                n_ctx=4096,                        # 4096-token context window
                n_threads=os.cpu_count() or 4,    # use all CPU cores
                n_gpu_layers=0,                   # set to 35 for NVIDIA GPU
                verbose=False
            )
            self.use_phi3 = True
            print("[LLM] Phi-3 Mini ready.")
        except ImportError:
            print("[LLM] llama-cpp-python not installed. "
                  "Run: pip install llama-cpp-python")
            self._load_t5()
        except Exception as exc:
            print(f"[LLM] Phi-3 load error: {exc}. Falling back to flan-t5.")
            self._load_t5()

    def _load_t5(self):
        """Load flan-t5-base as a lightweight fallback."""
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        t5_model = "google/flan-t5-base"
        self.tokenizer = AutoTokenizer.from_pretrained(t5_model)
        self.t5_model  = AutoModelForSeq2SeqLM.from_pretrained(t5_model)
        self.use_phi3  = False
        print("[LLM] flan-t5-base loaded (fallback — limited quality).")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def answer_question(self, question: str) -> Tuple[str, List[Dict]]:
        """
        Retrieve relevant chunks and generate an answer.

        Args:
            question: Natural-language user question.

        Returns:
            Tuple of:
              - answer  (str)
              - sources (List[Dict]) — each has keys: text, page, source, rerank_score
        """
        if not question.strip():
            return "Please provide a question.", []

        lowq = question.lower().strip()

        # ── Direct responses (no retrieval needed) ──────────────────────
        greetings = {"hi", "hello", "hey", "how are you"}
        if lowq in greetings:
            return ("Hello! I am your document assistant. "
                    "Upload a PDF and ask me anything about it."), []

        help_triggers = ["what can i ask", "how to use", "capabilities", "guide me"]
        if any(k in lowq for k in help_triggers):
            return (
                "You can ask me:\n"
                "- **Summaries**: 'Summarize the document' or 'What is this about?'\n"
                "- **Specific facts**: names, dates, figures from the document\n"
                "- **Tables**: 'What values are in the table on page 3?'\n"
                "- **Images**: 'Describe the image on page 5'\n"
                "- **Comparisons**: 'Compare X and Y from the document'"
            ), []

        # ── Hybrid retrieval ─────────────────────────────────────────────
        chunks = self.retriever.retrieve(question, top_k=4)

        if not chunks:
            context = "No relevant content found in the document."
        else:
            parts = [f"[Page {c['page']}] {c['text']}" for c in chunks]
            context = "\n\n---\n\n".join(parts)

        # ── Generate ─────────────────────────────────────────────────────
        if self.use_phi3:
            answer = self._generate_phi3(question, context)
        else:
            answer = self._generate_t5(question, context)

        return answer, chunks

    # ------------------------------------------------------------------
    # Generation backends
    # ------------------------------------------------------------------

    def _generate_phi3(self, question: str, context: str) -> str:
        """Phi-3 Mini with ChatML-format prompt."""
        system_msg = (
            "You are a precise document assistant. "
            "Answer questions strictly based on the provided document context. "
            "Always cite the page number when referencing information "
            "(e.g. 'According to page 3...'). "
            "If the answer is not in the context, say: "
            "'I could not find that in the document.' "
            "Be concise and accurate."
        )
        user_msg = (
            f"Document Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )

        # Build ChatML prompt from token variables (no raw special tokens in source)
        prompt = (
            f"{_SYS_OPEN}\n{system_msg}{_SYS_END}\n"
            f"{_USR_OPEN}\n{user_msg}{_SYS_END}\n"
            f"{_ASST_OPEN}\n"
        )

        result = self.llm(
            prompt,
            max_tokens=512,
            temperature=0.2,          # low = factual, focused output
            repeat_penalty=1.1,
            stop=[_USR_OPEN, _SYS_OPEN]  # stop before next turn starts
        )
        return result["choices"][0]["text"].strip()

    def _generate_t5(self, question: str, context: str) -> str:
        """flan-t5-base fallback generation with intent-aware prompting."""
        lowq = question.lower()

        if any(k in lowq for k in ["summarize", "summary", "about", "overview", "explain"]):
            instruction = "Summarize the main topic and key points based on the context."
        elif any(k in lowq for k in ["author", "who wrote", "who is"]):
            instruction = "Extract the author names from the context. Ignore publishers or dates."
        else:
            instruction = "Use the context to answer the question accurately and completely."

        prompt = (
            f"You are a document assistant. {instruction} "
            f"If the answer is not in the context, say: "
            f"'I could not find that in the document.'\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\nAnswer:"
        )

        inputs = self.tokenizer(
            prompt, return_tensors="pt", max_length=1024, truncation=True
        )
        outputs = self.t5_model.generate(
            inputs.input_ids,
            max_length=200,
            min_length=5,
            num_beams=4,
            repetition_penalty=1.2,
            length_penalty=1.0,
            early_stopping=True
        )
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer.strip() or "Unable to generate an answer."
