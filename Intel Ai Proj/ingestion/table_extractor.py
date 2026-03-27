"""
Table extractor: converts pdfplumber table (list of lists) into a
human-readable text representation suitable for RAG embedding.
"""
from typing import List


def table_to_text(table: List[List], page_num: int) -> str:
    """
    Convert a pdfplumber table to natural language for RAG injection.

    Input:  [["Name", "Score"], ["Alice", "95"], ["Bob", "87"]]
    Output:
        Table on page 2 with columns: Name, Score.
        Row: Name=Alice, Score=95
        Row: Name=Bob, Score=87

    Args:
        table: nested list (rows x cols), first row is headers
        page_num: page number for attribution

    Returns:
        Readable string representation
    """
    if not table or not table[0]:
        return ""

    headers = [str(h).strip() if h else f"Col{idx}" for idx, h in enumerate(table[0])]
    lines = [f"Table on page {page_num} with columns: {', '.join(headers)}."]

    for row in table[1:]:
        if not row:
            continue
        pairs = [
            f"{h}={str(v).strip()}"
            for h, v in zip(headers, row)
            if v and str(v).strip()
        ]
        if pairs:
            lines.append("Row: " + ", ".join(pairs))

    return "\n".join(lines)
