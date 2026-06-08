# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

"Minimizing Out-of-Pocket Cost for College Students" covers the full ecosystem of free and subsidized resources available to enrolled students — federal grants, merit scholarships, work-study jobs, paid research positions, food assistance programs, emergency funds, and financial aid appeal strategies. This knowledge is genuinely hard to find because it is fragmented across official government portals, nonprofit program pages, scholarship databases, and student community forums — and the most actionable insights (which programs pay quickly, which appeals succeed, which campus resources most students never discover) live in peer-written Reddit threads and student testimonials rather than any single official guide. A student who knows how to stack these resources can dramatically reduce what they pay out of pocket, but most never learn the full picture exists.

---

## Documents

1. **Federal Pell Grants — StudentAid.gov**
   Official eligibility rules, maximum award amounts, and application process for the largest federal grant program.
   https://studentaid.gov/understand-aid/types/grants/pell

2. **Federal Work-Study — StudentAid.gov**
   How work-study is awarded, types of eligible jobs, earning limits, and FAFSA requirements.
   https://studentaid.gov/understand-aid/types/work-study

3. **8 Things About Work-Study — StudentAid.gov**
   Practical student-facing tips on finding, accepting, and balancing work-study jobs.
   https://studentaid.gov/articles/8-things-federal-work-study/

4. **NSF REU for Students — NSF.gov**
   Paid undergraduate research opportunities nationwide, stipend details, eligibility, and how to apply.
   https://www.nsf.gov/funding/initiatives/reu/students

5. **SNAP for College Students — USDA**
   Federal food assistance eligibility rules and exemptions specific to students enrolled at least half-time.
   https://www.fns.usda.gov/snap/students

6. **UNCF Emergency Student Aid**
   Emergency grants up to $2,500 for students at HBCU institutions facing sudden hardship.
   https://uncf.org/pages/cesa

7. **Swipe Out Hunger / CUFBA**
   Campus food pantry network supporting 800+ institutions; microgrant fund for student food insecurity.
   https://swipehunger.org/cufba

8. **Financial Aid Appeal Letter — NerdWallet**
   Step-by-step guide to writing an effective financial aid appeal, including what circumstances actually work.
   https://www.nerdwallet.com/student-loans/learn/financial-aid-appeal-letter

9. **Emergency Grants for College Students — SoFi**
   Overview of emergency grant programs across UNCF, Scholarship America, College Success Foundation, and campus offices.
   https://www.sofi.com/learn/content/emergency-grants-college/

10. **r/financialaid — Reddit**
    Student-shared FAFSA outcomes, aid appeal results, award letter comparisons, and financial aid office experiences.
    https://www.reddit.com/r/financialaid/

---

## Chunking Strategy

**Chunk size:** 400 tokens

**Overlap:** 50 tokens

**Reasoning:** Most sources are medium-to-long guides (800–2,500 words) with key facts — grant amounts, eligibility rules, deadlines — scattered across sections rather than concentrated in one place. Fixed-size chunking at 400 tokens with 50-token overlap preserves enough context so that an eligibility condition (e.g., "must work 20 hours per week") stays near the program name it belongs to, while keeping chunks small enough for precise retrieval. Before chunking, commercial pages (NerdWallet, SoFi) are pre-processed to strip navigation, footers, and promotional ad sections. Reddit posts are collected as one document per thread (original post body + top 5 comments) and chunked as plain prose. Database landing pages (Fastweb, Bold.org) are not chunked at the homepage level — individual scholarship listing pages are collected instead, since the homepage itself contains minimal extractable text.

**Final chunk count:** 51 chunks across 10 documents

---

## Retrieval Approach

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers (local inference, no API key required)

**Top-k:** 5

**Production tradeoff reflection:** all-MiniLM-L6-v2 is fast, free, and runs entirely locally — the right choice for a student project with no API budget. In a real production deployment, the tradeoffs would be: (1) Context length — MiniLM handles 256 tokens max per chunk, which may truncate longer passages; a model like OpenAI's text-embedding-3-small handles 8,191 tokens. (2) Domain accuracy — a general-purpose model may not rank financial aid jargon (EFC, SAI, FSEOG, dependency override) as precisely as a finance-tuned model would. (3) Multilingual support — irrelevant for this corpus but critical for a diverse student population at an international university. (4) Latency — local inference adds roughly 50ms per query versus under 10ms for a hosted API at scale. (5) Cost — API-hosted embeddings ($0.00002 per 1K tokens for OpenAI) may be cheaper than the infrastructure cost of running local inference across millions of queries.

---

## Plan

1. **Q:** What is the maximum Pell Grant award for 2026–27, and what factors determine how much a student receives?
   **Expected:** $7,395 maximum; amount depends on financial need, family size, enrollment status (full vs. half-time), and federal poverty guidelines.

2. **Q:** Can a college student enrolled half-time qualify for SNAP food benefits, and what exemptions allow it?
   **Expected:** Generally no — but exemptions apply for students who work 20+ hours/week in paid employment, participate in a work-study program, are under 18 or 50+, or care for a child under age 6.

3. **Q:** What specific elements must a financial aid appeal letter contain?
   **Expected:** A named contact at the financial aid office, an explanation of changed circumstances (income drop, medical emergency, or divorce), the exact dollar amount being requested, supporting documents that back up the claim, and a total length of no more than one page.

4. **Q:** What does the NSF REU program provide to students, and what is the maximum funding amount for a CISE REU supplement?
   **Expected:** NSF REU (Research Experiences for Undergraduates) provides paid research positions at universities; participants receive a stipend and in many cases housing, meals, and travel support. The maximum for a CISE REU supplement is $10,000 per student per year.

5. **Q:** What emergency grant programs exist for students who suddenly cannot afford to stay enrolled?
   **Expected:** UNCF Emergency Student Aid (up to $2,500 for HBCU students), Scholarship America Emergency Aid, College Success Foundation Emergency Fund (up to $500/year), and institution-specific emergency funds available through most campus financial aid offices.

---

## Anticipated Challenges

1. **Key facts split across chunk boundaries**: Grant amounts, eligibility conditions, and application steps are spread across paragraphs in most sources rather than concentrated in one section. A chunk boundary mid-paragraph could separate "students must work 20 hours per week" from the SNAP exemption context it belongs to, causing the retriever to return incomplete or misleading fragments. Mitigation: use header-based splitting where possible, and keep overlap at 50 tokens to preserve cross-boundary context.

2. **Reddit post quality variance**: High-upvote Reddit threads contain genuine student experience and practical advice, but individual posts range from detailed and accurate to anecdotal and outdated. The system has no mechanism to verify whether a specific Reddit claim (e.g., "my school emergency fund sent me $500 in two days") is generalizable or a one-off. This may cause the LLM to present outlier experiences as typical. Mitigation: during collection, prefer threads with high upvote counts and multiple corroborating comments over single low-engagement posts.

---

## Architecture

```
Documents (20 sources: gov pages, nonprofit guides, Reddit threads)
          │
          ▼
┌─────────────────────┐
│   1. Ingestion      │  Fetch raw text from URLs and Reddit threads
│                     │  Strip HTML, nav, footers, ad sections
│                     │  Reddit: post body + top 5 comments = 1 doc
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   2. Chunking       │  Header-based splitting for structured guides
│                     │  400-token chunks, 50-token overlap
│                     │  Library: custom Python + tiktoken
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  3. Embedding +     │  Model: all-MiniLM-L6-v2 (sentence-transformers)
│     Vector Store    │  Store: ChromaDB (local)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   4. Retrieval      │  Query → embed → cosine similarity search
│                     │  Return top-k = 5 chunks with metadata
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   5. Generation     │  LLM: Groq API (llama3 or mixtral)
│                     │  System prompt: answer only from retrieved
│                     │  chunks, cite sources, say "I don't know"
│                     │  if the corpus doesn't cover the question
└─────────┬───────────┘
          │
          ▼
     Answer + source citations
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
Give Claude the Chunking Strategy section of this planning.md and ask it to implement `chunk_text(text, chunk_size=400, overlap=50)` using token-aware splitting with tiktoken. Also ask it to implement `ingest_document(url)` that fetches a URL, strips HTML boilerplate, and returns clean plain text. Verify output by printing chunk boundaries against a known source document and confirming no chunk splits an eligibility rule from its program name.

**Milestone 4 — Embedding and retrieval:**
Give Claude the Retrieval Approach section and ask it to implement `embed_and_store(chunks, metadata)` using sentence-transformers + ChromaDB, and `retrieve(query, k=5)` returning the top-5 chunks with their source metadata. Verify by running all 5 evaluation questions through the retriever and confirming the returned chunks contain the expected keywords (e.g., "$7,395" for question 1, "20 hours" for question 2).

**Milestone 5 — Generation and interface:**
Give Claude the Architecture section and the 5 evaluation questions, then ask it to implement `generate_answer(query, chunks)` using the Groq API with a system prompt that enforces grounding. Verify that responses cite sources by name and return a clear "I don't have enough information" message for questions outside the corpus (e.g., "What is the best dorm at UCLA?").




