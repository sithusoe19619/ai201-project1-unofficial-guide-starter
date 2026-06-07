"""
pipeline.py — orchestrator for Milestone 3.

Stages:
  1. Fetch + clean all 10 sources (ingest.py)
  2. Manual inspection pause — read first 3,000 chars of pell_grants
  3. Chunk all cleaned documents (chunk.py)
  4. Print 5 representative sample chunks for manual review
  5. Save all chunks to documents/chunks.json
  6. Print summary
"""

import json
import random

from ingest import run_ingest
from chunk import make_chunks

CHUNKS_PATH = "documents/chunks.json"
INSPECT_SOURCE = "pell_grants"
SAMPLE_COUNT = 5


def _inspect_pause(cleaned: list[dict]) -> None:
    print("\n" + "=" * 60)
    print("STAGE 2 — MANUAL INSPECTION")
    print("=" * 60)

    target = next(
        (item for item in cleaned if item["source"]["name"] == INSPECT_SOURCE),
        cleaned[0] if cleaned else None,
    )
    if target is None:
        print("  No documents to inspect.")
        return

    name = target["source"]["name"]
    preview = target["clean_text"][:3000]
    print(f"\n  First 3,000 chars of [{name}]:\n")
    print(preview)
    print("\n" + "-" * 60)
    input("  Press Enter to continue to chunking...")


def _sample_chunks(all_chunks: list[dict]) -> None:
    print("\n" + "=" * 60)
    print("STAGE 4 — CHUNK INSPECTION (5 samples)")
    print("=" * 60)

    # Pick one per source type where possible, then fill randomly
    by_type: dict[str, list[dict]] = {}
    for chunk in all_chunks:
        t = chunk["metadata"]["source_type"]
        by_type.setdefault(t, []).append(chunk)

    samples = []
    for t, chunks in by_type.items():
        samples.append(random.choice(chunks))
        if len(samples) >= SAMPLE_COUNT:
            break

    while len(samples) < SAMPLE_COUNT and len(all_chunks) > len(samples):
        candidate = random.choice(all_chunks)
        if candidate not in samples:
            samples.append(candidate)

    for i, chunk in enumerate(samples, 1):
        m = chunk["metadata"]
        print(f"\n  --- Sample {i}/{SAMPLE_COUNT} ---")
        print(f"  Source : {m['source_name']}  ({m['source_type']})")
        print(f"  Chunk  : {m['chunk_index'] + 1}/{m['total_chunks']}  |  {m['token_count']} tokens")
        print()
        print(chunk["text"])
        print()
        if i < SAMPLE_COUNT:
            input("  Press Enter for next sample...")


def main() -> None:
    # Stage 1
    cleaned = run_ingest()

    if not cleaned:
        print("\n✗ No documents were ingested. Check manual fallback instructions above.")
        return

    # Stage 2
    _inspect_pause(cleaned)

    # Stage 3
    print("\n" + "=" * 60)
    print("STAGE 3 — CHUNK")
    print("=" * 60)

    all_chunks: list[dict] = []
    for item in cleaned:
        source = item["source"]
        chunks = make_chunks(source, item["clean_text"])
        print(f"  [{source['name']}] → {len(chunks)} chunks")
        all_chunks.extend(chunks)

    print(f"\n→ {len(all_chunks)} total chunks across {len(cleaned)} documents\n")

    # Stage 4
    _sample_chunks(all_chunks)

    # Stage 5
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    # Stage 6
    print("\n" + "=" * 60)
    print("STAGE 5 — SUMMARY")
    print("=" * 60)
    print(f"  Documents processed : {len(cleaned)}/{10}")
    print(f"  Total chunks        : {len(all_chunks)}")
    print(f"  Chunks saved to     : {CHUNKS_PATH}")

    by_source = {}
    for c in all_chunks:
        n = c["metadata"]["source_name"]
        by_source[n] = by_source.get(n, 0) + 1
    print("\n  Per-source breakdown:")
    for name, count in by_source.items():
        print(f"    {name:<25} {count} chunks")

    print("\n✓ Milestone 3 complete. Run embed.py (Milestone 4) next.\n")


if __name__ == "__main__":
    main()
