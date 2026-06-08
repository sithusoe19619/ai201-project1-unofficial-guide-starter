"""
test_retrieval.py — run all 5 evaluation queries and print results.

Run after embed.py has been run at least once:
    python test_retrieval.py
"""

from embed import retrieve

EVAL_QUERIES = [
    (1, "What is the maximum Pell Grant award for 2026–27, and what factors determine how much a student receives?"),
    (2, "Can a college student enrolled half-time qualify for SNAP food benefits, and what exemptions allow it?"),
    (3, "What specific elements must a financial aid appeal letter contain?"),
    (4, "What does the NSF REU program provide to students, and what is the maximum funding amount for a CISE REU supplement?"),
    (5, "What emergency grant programs exist for students who suddenly cannot afford to stay enrolled?"),
]

for num, query in EVAL_QUERIES:
    print(f"\n{'=' * 60}")
    print(f"Q{num}: {query}")
    print("=" * 60)
    results = retrieve(query, k=5)
    for rank, r in enumerate(results, 1):
        m = r["metadata"]
        print(
            f"\n  [{rank}] distance={r['distance']}  "
            f"source={m['source_name']}  "
            f"chunk={m['chunk_index'] + 1}/{m['total_chunks']}"
        )
        print(f"       {r['text'][:300]}")
    print()
