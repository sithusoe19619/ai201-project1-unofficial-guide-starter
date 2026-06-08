"""
generate.py — Milestone 5: grounded generation with Groq.

Run end-to-end test (3 in-corpus + 1 out-of-corpus query):
    python generate.py

Import ask() in app.py for the Gradio interface.
"""

import os
from groq import Groq
from dotenv import load_dotenv
from embed import retrieve

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """\
You are a financial aid assistant for college students.
Answer the user's question using ONLY the document excerpts provided below.
Do not use your general training knowledge under any circumstances.
If the excerpts do not contain enough information to answer the question, \
respond with exactly: "I don't have enough information on that based on my available documents."
When you use information, mention the source name shown before each excerpt.
Be specific — cite exact figures, eligibility rules, and dollar amounts as they appear in the text.\
"""


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        m = chunk["metadata"]
        header = f"Document {i} (source: {m['source_name']} | {m['source_url']}):"
        parts.append(f"{header}\n{chunk['text']}")
    return "\n\n".join(parts)


def _dedupe_sources(chunks: list[dict]) -> list[str]:
    seen = set()
    sources = []
    for chunk in chunks:
        m = chunk["metadata"]
        label = f"{m['source_name']} — {m['source_url']}"
        if label not in seen:
            seen.add(label)
            sources.append(label)
    return sources


def ask(query: str, k: int = 5) -> dict:
    """
    End-to-end RAG: retrieve → generate → return answer + sources.

    Sources are collected from chunk metadata before the LLM call so
    attribution is guaranteed regardless of what the model says.

    Returns:
        {"answer": str, "sources": list[str]}
    """
    chunks = retrieve(query, k=k)

    # Programmatic attribution — always present, independent of LLM output
    sources = _dedupe_sources(chunks)

    context = _build_context(chunks)
    user_message = f"Documents:\n{context}\n\nQuestion: {query}"

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content
    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    test_queries = [
        "What is the maximum Pell Grant award for 2026–27, and what factors determine how much a student receives?",
        "Can a college student enrolled half-time qualify for SNAP food benefits, and what exemptions allow it?",
        "What specific elements must a financial aid appeal letter contain?",
        "What are the best dorms at UCLA?",  # out-of-corpus — should refuse
    ]

    for q in test_queries:
        print(f"\n{'=' * 60}")
        print(f"Q: {q}")
        print("=" * 60)
        result = ask(q)
        print(f"Answer:\n{result['answer']}")
        print("\nSources:")
        for s in result["sources"]:
            print(f"  • {s}")
