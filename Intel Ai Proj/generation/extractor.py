import re
import logging
from typing import List, Dict, Optional

# Setup logging
logger = logging.getLogger("rag_extraction")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def classify_query(query: str) -> str:
    """Classify querying into factual (exact answer) or descriptive (explanation)."""
    low_q = query.lower()
    factual_keywords = [
        "when", "where", "who", "whose", "how many", "how much", 
        "date", "time", "number", "id", "code", "name", "venue", 
        "location", "amount", "total", "roll number"
    ]
    if any(k in low_q for k in factual_keywords):
        return "factual"
    return "descriptive"

def extract_exact_answer(query: str, chunks: List[Dict]) -> Optional[str]:
    """Pattern matching for exact extraction on factual queries."""
    low_q = query.lower()
    
    # Define regex patterns based on keywords in query
    pattern = None
    if "roll number" in low_q or "id" in low_q or "code" in low_q:
        pattern = r'\b[A-Z0-9]{5,15}\b'
    elif "date" in low_q or "when" in low_q:
        pattern = r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}(?:st|nd|rd|th)?,? \d{4})\b'
    elif "time" in low_q:
        pattern = r'\b(?:[01]?\d|2[0-3]):[0-5]\d\s?(?:AM|PM|am|pm)?\b'
    elif "amount" in low_q or "total" in low_q or "price" in low_q or "how much" in low_q:
        pattern = r'\$\s?\d+(?:,\d{3})*(?:\.\d{2})?'
        
    if not pattern:
        return None
        
    logger.info(f"Factual query detected. Using pattern: {pattern}")
    
    compiled = re.compile(pattern, re.IGNORECASE)
    
    # Search chunks heavily matched to top docs
    for c in chunks:
        # Sort sentences in chunk so we extract closest match if needed, but here we just regex the whole chunk.
        # Find all matches
        matches = compiled.findall(c['text'])
        if matches:
            # multiple found -> return best match only
            best_match = matches[0] 
            logger.info(f"Extracted answer: {best_match}")
            return best_match
            
    return None

def filter_context(query: str, chunks: List[Dict]) -> List[Dict]:
    """Filter sentences to only those containing query synonyms/keywords."""
    stop_words = {"what", "is", "the", "a", "an", "of", "in", "to", "for", "with", "on", "at", "by", "from", "how", "many", "much", "explain", "describe", "about"}
    keywords = [w for w in re.sub(r'[^\w\s]', '', query.lower()).split() if w not in stop_words and len(w) > 2]
    
    if not keywords:
        return chunks
        
    filtered_chunks = []
    
    for c in chunks:
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', c['text'])
        relevant_sentences = []
        
        for s in sentences:
            sl = s.lower()
            if any(kw in sl for kw in keywords):
                relevant_sentences.append(s)
                
        if relevant_sentences:
            filtered_chunks.append({
                "page": c["page"],
                "text": " ".join(relevant_sentences),
                "source": c.get("source", ""),
                "rerank_score": c.get("rerank_score", 0.0)
            })
            
    # Fallback if too strict
    return filtered_chunks if filtered_chunks else chunks
