"""
chunk.py — token-aware chunking with tiktoken.
"""

import tiktoken

ENCODING = tiktoken.get_encoding("cl100k_base")
MIN_CHUNK_TOKENS = 20


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """Sliding window over token list. Returns list of decoded chunk strings."""
    tokens = ENCODING.encode(text)
    if not tokens:
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        if len(chunk_tokens) >= MIN_CHUNK_TOKENS:
            chunks.append(ENCODING.decode(chunk_tokens))
        if end >= len(tokens):
            break
        start += step

    return chunks


def make_chunks(source: dict, clean_text: str) -> list[dict]:
    """Return list of chunk dicts with full metadata."""
    raw_chunks = chunk_text(clean_text)
    total = len(raw_chunks)
    result = []
    for i, text in enumerate(raw_chunks):
        result.append({
            "text": text,
            "metadata": {
                "source_name": source["name"],
                "source_url": source["url"],
                "source_type": source["type"],
                "chunk_index": i,
                "total_chunks": total,
                "token_count": len(ENCODING.encode(text)),
            },
        })
    return result
