# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

"Minimizing Out-of-Pocket Cost for College Students" covers the full ecosystem of free and subsidized resources available to enrolled students — federal grants, merit scholarships, work-study jobs, paid research positions, food assistance programs, emergency funds, and financial aid appeal strategies. This knowledge is genuinely hard to find because it is fragmented across official government portals, nonprofit program pages, scholarship databases, and student community forums — and the most actionable insights (which programs pay quickly, which appeals succeed, which campus resources most students never discover) live in peer-written Reddit threads and student testimonials rather than any single official guide. A student who knows how to stack these resources can dramatically reduce what they pay out of pocket, but most never learn the full picture exists.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Federal Pell Grants — StudentAid.gov | Official government guide | https://studentaid.gov/understand-aid/types/grants/pell |
| 2 | Federal Work-Study — StudentAid.gov | Official government guide | https://studentaid.gov/understand-aid/types/work-study |
| 3 | 8 Things About Work-Study — StudentAid.gov | Official government article | https://studentaid.gov/articles/8-things-federal-work-study/ |
| 4 | NSF REU for Students — NSF.gov | Official government program page | https://www.nsf.gov/funding/initiatives/reu/students |
| 5 | SNAP for College Students — USDA | Official government policy page | https://www.fns.usda.gov/snap/students |
| 6 | UNCF Emergency Student Aid | Nonprofit program page | https://uncf.org/pages/cesa |
| 7 | Swipe Out Hunger / CUFBA | Nonprofit organization page | https://swipehunger.org/cufba |
| 8 | Financial Aid Appeal Letter — NerdWallet | Financial media guide | https://www.nerdwallet.com/student-loans/learn/financial-aid-appeal-letter |
| 9 | Emergency Grants for College Students — SoFi | Financial media guide | https://www.sofi.com/learn/content/emergency-grants-college/ |
| 10 | r/financialaid — Reddit | Student community forum | https://www.reddit.com/r/financialaid/ |

---

## Chunking Strategy

**Chunk size:** 400 tokens

**Overlap:** 50 tokens

**Why these choices fit your documents:** Most sources are medium-to-long guides (800–2,500 words) with key facts — grant amounts, eligibility rules, deadlines — scattered across sections rather than concentrated in one place. Chunks of 400 tokens preserve enough context so an eligibility condition stays near the program name it belongs to, while remaining small enough for precise retrieval. The 50-token overlap prevents information from being lost at boundaries. Before chunking, commercial pages are pre-processed to strip navigation, footers, and promotional sections. Reddit posts are collected as one document per thread (original post + top 5 comments) and chunked as plain prose.

**Final chunk count:** (to be filled after ingestion is complete)

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (local inference, no API key required)

**Production tradeoff reflection:** all-MiniLM-L6-v2 is fast, free, and runs entirely locally — the right choice for a student project with no API budget. In a real production deployment, the tradeoffs would be: (1) Context length — MiniLM handles 256 tokens max per chunk, which may truncate longer passages; a model like OpenAI's text-embedding-3-small handles 8,191 tokens. (2) Domain accuracy — a general-purpose model may not rank financial aid jargon (EFC, SAI, FSEOG, dependency override) as precisely as a finance-tuned model. (3) Multilingual support — irrelevant for this corpus but critical for a diverse student population. (4) Latency — local inference adds roughly 50ms per query versus under 10ms for a hosted API at scale. (5) Cost — API-hosted embeddings ($0.00002 per 1K tokens for OpenAI) may ultimately be cheaper than infrastructure costs for local inference at millions of queries.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
