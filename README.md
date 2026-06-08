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

1. **Federal Pell Grants — StudentAid.gov** *(Official government guide)*
   https://studentaid.gov/understand-aid/types/grants/pell

2. **Federal Work-Study — StudentAid.gov** *(Official government guide)*
   https://studentaid.gov/understand-aid/types/work-study

3. **8 Things About Work-Study — StudentAid.gov** *(Official government article)*
   https://studentaid.gov/articles/8-things-federal-work-study/

4. **NSF REU for Students — NSF.gov** *(Official government program page)*
   https://www.nsf.gov/funding/initiatives/reu/students

5. **SNAP for College Students — USDA** *(Official government policy page)*
   https://www.fns.usda.gov/snap/students

6. **UNCF Emergency Student Aid** *(Nonprofit program page)*
   https://uncf.org/pages/cesa

7. **Swipe Out Hunger / CUFBA** *(Nonprofit organization page)*
   https://swipehunger.org/cufba

8. **Financial Aid Appeal Letter — NerdWallet** *(Financial media guide)*
   https://www.nerdwallet.com/student-loans/learn/financial-aid-appeal-letter

9. **Emergency Grants for College Students — SoFi** *(Financial media guide)*
   https://www.sofi.com/learn/content/emergency-grants-college/

10. **r/financialaid — Reddit** *(Student community forum)*
    https://www.reddit.com/r/financialaid/

---

## Chunking Strategy

**Chunk size:** 400 tokens

**Overlap:** 50 tokens

**Why these choices fit your documents:** Most sources are medium-to-long guides (800–2,500 words) with key facts — grant amounts, eligibility rules, deadlines — scattered across sections rather than concentrated in one place. Chunks of 400 tokens preserve enough context so an eligibility condition stays near the program name it belongs to, while remaining small enough for precise retrieval. The 50-token overlap prevents information from being lost at boundaries. Before chunking, commercial pages are pre-processed to strip navigation, footers, and promotional sections. Reddit posts are collected as one document per thread (original post + top 5 comments) and chunked as plain prose.

**Final chunk count:** 51 chunks across 10 documents (2–4 per government source, 3–6 per nonprofit/commercial, 19 from Reddit)

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (local inference, no API key required)

**Production tradeoff reflection:** all-MiniLM-L6-v2 is fast, free, and runs entirely locally — the right choice for a student project with no API budget. In a real production deployment, the tradeoffs would be: (1) Context length — MiniLM handles 256 tokens max per chunk, which may truncate longer passages; a model like OpenAI's text-embedding-3-small handles 8,191 tokens. (2) Domain accuracy — a general-purpose model may not rank financial aid jargon (EFC, SAI, FSEOG, dependency override) as precisely as a finance-tuned model. (3) Multilingual support — irrelevant for this corpus but critical for a diverse student population. (4) Latency — local inference adds roughly 50ms per query versus under 10ms for a hosted API at scale. (5) Cost — API-hosted embeddings ($0.00002 per 1K tokens for OpenAI) may ultimately be cheaper than infrastructure costs for local inference at millions of queries.

---

## Grounded Generation

**System prompt grounding instruction:**

> "You are a financial aid assistant for college students. Answer the user's question using ONLY the document excerpts provided below. Do not use your general training knowledge under any circumstances. If the excerpts do not contain enough information to answer the question, respond with exactly: 'I don't have enough information on that based on my available documents.' When you use information, mention the source name shown before each excerpt. Be specific — cite exact figures, eligibility rules, and dollar amounts as they appear in the text."

The system prompt does three things: (1) prohibits the model from using general training knowledge, (2) mandates a specific refusal phrase for out-of-corpus questions so the model cannot improvise a plausible-sounding answer, and (3) labels each retrieved chunk with its source name so the model can cite naturally in its response.

Each chunk is passed to the model as a labeled block: `Document N (source: <name> | <url>): <chunk text>`, so citation in the response can be verified against the retrieved context.

**How source attribution is surfaced in the response:**

Sources are collected programmatically from the retrieved chunk metadata (`source_name` + `source_url`) **before** the Groq API call. The `_dedupe_sources()` function deduplicates them while preserving order, producing a list like `["pell_grants — https://studentaid.gov/...", ...]`. This list is always returned from `ask()` and displayed in the Gradio UI's "Sources retrieved" box, regardless of whether the model mentions them in its answer text. Attribution is guaranteed by the pipeline — not left to the LLM.

---

## Evaluation Report

1. **Q:** What is the maximum Pell Grant award for 2026–27, and what factors determine how much a student receives?
   **Expected answer:** $7,395 maximum; amount depends on financial need, family size, enrollment status (full vs. half-time), and federal poverty guidelines.
   **System response:** "The maximum Federal Pell Grant award for the 2026-27 award year is $7,395. The amount a student receives depends on several factors, including: (1) their Student Aid Index based on their FAFSA form, (2) the cost of attendance determined by their school, (3) their status as a full-time or part-time student, (4) their plans to attend school for a full academic year or less, and (5) their remaining Pell eligibility under their Pell lifetime eligibility used (LEU) amount."
   **Retrieval quality:** Relevant
   **Response accuracy:** Accurate

2. **Q:** Can a college student enrolled half-time qualify for SNAP food benefits, and what exemptions allow it?
   **Expected answer:** Generally no — but exemptions apply for students who work 20+ hours/week in paid employment, participate in a work-study program, are under 18 or 50+, or care for a child under age 6.
   **System response:** The system returned all 10 SNAP exemptions verbatim from the USDA source, including the 20-hours/week paid employment rule, work-study participation, age thresholds (under 18 or 50+), on-the-job training programs, child care for children under 6, single parents enrolled full-time with children under 12, TANF recipients, and SNAP E&T program participants.
   **Retrieval quality:** Relevant
   **Response accuracy:** Accurate

3. **Q:** What specific elements must a financial aid appeal letter contain?
   **Expected answer:** A named contact at the financial aid office, an explanation of changed circumstances (income drop, medical emergency, or divorce), the exact dollar amount being requested, supporting documents that back up the claim, and a total length of no more than one page.
   **System response:** The system returned 8 elements: address to a specific person, a clear ask with a specific reason, details of special circumstances, appropriate documentation, an exact dollar amount, a competing offer if available, next steps in the process, and opening and closing with gratitude.
   **Retrieval quality:** Relevant
   **Response accuracy:** Accurate

4. **Q:** What does the NSF REU program provide to students, and what is the maximum funding amount for a CISE REU supplement?
   **Expected answer:** NSF REU provides paid research positions at universities; participants receive a stipend and in many cases housing, meals, and travel support. The maximum for a CISE REU supplement is $10,000 per student per year.
   **System response:** "The NSF REU program provides students with competitive stipends and assistance with housing, meals, and travel. However, the maximum funding amount for a CISE REU supplement is not specified in the provided documents. The documents only mention that REU participants receive competitive stipends and assistance, but they do not provide information on the maximum funding amount for a CISE REU supplement."
   **Retrieval quality:** Partially relevant
   **Response accuracy:** Partially accurate

5. **Q:** What emergency grant programs exist for students who suddenly cannot afford to stay enrolled?
   **Expected answer:** UNCF Emergency Student Aid (up to $2,500 for HBCU students), Scholarship America Emergency Aid, College Success Foundation Emergency Fund (up to $500/year), and institution-specific emergency funds available through most campus financial aid offices.
   **System response:** The system returned all four expected programs plus additional detail: UNCF Emergency Student Aid with six specific funding options (Degree Completion Aid up to $2,500, Emergency Retention Grants up to $1,000, Emergency Loans up to $500, Food Insecurity Grants, Housing Insecurity Payments, and Natural Disaster Relief Fund), Scholarship America Emergency Aid, College Success Foundation Emergency Fund up to $500 per academic year, and institution-specific programs.
   **Retrieval quality:** Relevant
   **Response accuracy:** Accurate

---

## Failure Case Analysis

**Question that failed:** What does the NSF REU program provide to students, and what is the maximum funding amount for a CISE REU supplement?

**What the system returned:** The system correctly described what the REU program provides (competitive stipends, housing, meals, and travel support), but explicitly stated that "the maximum funding amount for a CISE REU supplement is not specified in the provided documents." The $10,000 figure was never returned.

**Root cause (tied to a specific pipeline stage):** The failure spans two pipeline stages. First, at the **ingestion stage**: the source document (nsf.gov/funding/initiatives/reu/students) is the general REU student overview page, which describes overall program benefits but does not publish CISE-specific supplement caps. The $10,000 figure appears on a separate CISE-program page that was never collected — so no amount of retrieval improvement can surface a fact that was never ingested. Second, at the **retrieval stage**: even if the figure existed somewhere in the corpus, "CISE" is a domain-specific acronym (Computer and Information Science and Engineering) that appears nowhere else in the 51 chunks. The all-MiniLM-L6-v2 embedding model has no semantic anchor for it and treats the query "CISE REU supplement maximum" as a near-OOV (out-of-vocabulary) term, mapping it poorly to the nsf_reu chunks and surfacing irrelevant sources (UNCF, SoFi) instead.

**What you would change to fix it:** Add the CISE-specific NSF supplement page (nsf.gov/cise/reu) as a separate source during ingestion so the $10,000 figure is present in the corpus. For the retrieval problem more broadly, a hybrid retrieval approach combining BM25 keyword matching with semantic similarity would ensure that exact acronym matches surface even when the embedding model cannot resolve semantic similarity — BM25 would score "CISE" directly without needing a semantic representation.

---

## Spec Reflection

**One way the spec helped you during implementation:** The Chunking Strategy section's explicit instruction to truncate commercial pages at "Advertisement" markers was implemented exactly as written and had a direct impact on index quality. Without it, the NerdWallet financial aid appeal guide — which embeds loan comparison ads and navigation blocks throughout its HTML — would have produced over 30 chunks of irrelevant promotional content, drowning out the actual appeal guidance and skewing retrieval toward ad copy. Having that instruction in the spec meant the cleaning logic was scoped correctly from the start rather than discovered as a bug after retrieval results were inspected.

**One way your implementation diverged from the spec, and why:** The architecture diagram in planning.md specifies "20 sources" and explicitly lists Fastweb and Bold.org scholarship database pages as planned sources. In practice, both sites are JavaScript-rendered single-page applications — their scholarship listing content is loaded dynamically and does not appear in the raw HTML that BeautifulSoup can parse. Rather than attempt a headless browser solution, which would have added Selenium or Playwright as a dependency and significantly complicated the ingestion pipeline, those sources were dropped. The final corpus uses 10 sources instead of 20. This did not harm retrieval quality for the domain's core questions because the dropped sources covered scholarship discovery (a different sub-domain) rather than the grant, food assistance, and financial aid appeal topics the evaluation questions target.

---

## AI Usage

**Instance 1 — Document ingestion and chunking (Milestone 3)**

- *What I gave the AI:* The Chunking Strategy section of planning.md along with requirements for two functions: `ingest_document(url)` to fetch and clean HTML from a URL, and `chunk_text(text)` to split it into 400-token chunks with 50-token overlap using tiktoken.
- *What it produced:* A working ingest pipeline with BeautifulSoup HTML cleaning and tiktoken-based chunking. It also handled the "Advertisement" truncation for commercial sources and structured each chunk with source metadata.
- *What I changed or overrode:* Reddit's JSON API returned a 403 error. I directed Claude to switch to scraping old.reddit.com HTML directly instead of using the API. Claude also produced a pipeline stage numbering bug where STAGE 2 appeared twice — I caught it during review and directed it to be fixed. I also corrected the chunk count target: Claude initially tried to hit an arbitrary "50 chunks" threshold from the spec example, and I redirected it to base the count on actual document lengths rather than a target number.

**Instance 2 — Retrieval verification (Milestone 4)**

- *What I gave the AI:* The Retrieval Approach section of planning.md and instructions to implement `embed_and_store()` using sentence-transformers with ChromaDB, and `retrieve(query, k=5)` returning the top-k chunks with metadata and cosine distance scores.
- *What it produced:* A working `embed.py` with PersistentClient ChromaDB storage, lazy model loading, and a retrieve function that returns ranked results with distances.
- *What I changed or overrode:* Claude initially declared Milestone 4 complete after printing retrieval results, without explicitly verifying that expected keywords appeared in the chunk text. I pushed it to run a targeted keyword verification script that checked whether "$7,395", "20 hours", "specific person", "stipend", and "emergency" actually appeared in the text of the top-ranked chunks — not just that results were returned. Claude ran the script and confirmed all keywords were present before I accepted the milestone as done.
