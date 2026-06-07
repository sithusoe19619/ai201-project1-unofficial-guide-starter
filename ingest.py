"""
ingest.py — fetch and clean all 10 source documents.

Saves raw fetched text to documents/raw/ first (safety net), then
saves cleaned plain text to documents/clean/. If a raw file already
exists and is non-empty, the network call is skipped — paste text
manually into documents/raw/{filename}.txt and re-run to use it.
"""

import os
import re
import time
import json
import requests
from bs4 import BeautifulSoup

RAW_DIR = "documents/raw"
CLEAN_DIR = "documents/clean"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SOURCES = [
    {
        "name": "pell_grants",
        "url": "https://studentaid.gov/understand-aid/types/grants/pell",
        "filename": "pell_grants",
        "type": "government",
    },
    {
        "name": "work_study",
        "url": "https://studentaid.gov/understand-aid/types/work-study",
        "filename": "work_study",
        "type": "government",
    },
    {
        "name": "work_study_8things",
        "url": "https://studentaid.gov/articles/8-things-federal-work-study/",
        "filename": "work_study_8things",
        "type": "government",
    },
    {
        "name": "nsf_reu",
        "url": "https://www.nsf.gov/funding/initiatives/reu/students",
        "filename": "nsf_reu",
        "type": "government",
    },
    {
        "name": "snap_students",
        "url": "https://www.fns.usda.gov/snap/students",
        "filename": "snap_students",
        "type": "government",
    },
    {
        "name": "uncf_emergency",
        "url": "https://uncf.org/pages/cesa",
        "filename": "uncf_emergency",
        "type": "nonprofit",
    },
    {
        "name": "swipe_out_hunger",
        "url": "https://swipehunger.org/cufba",
        "filename": "swipe_out_hunger",
        "type": "nonprofit",
    },
    {
        "name": "nerdwallet_appeal",
        "url": "https://www.nerdwallet.com/student-loans/learn/financial-aid-appeal-letter",
        "filename": "nerdwallet_appeal",
        "type": "commercial",
    },
    {
        "name": "sofi_emergency",
        "url": "https://www.sofi.com/learn/content/emergency-grants-college/",
        "filename": "sofi_emergency",
        "type": "commercial",
    },
    {
        "name": "reddit_financialaid",
        "url": "https://www.reddit.com/r/financialaid/",
        "filename": "reddit_financialaid",
        "type": "reddit",
    },
]


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def fetch_reddit() -> str | None:
    """Fetch top posts from r/financialaid using the old Reddit JSON API."""
    listing_url = "https://old.reddit.com/r/financialaid/top.json?limit=10&t=year"
    try:
        resp = requests.get(listing_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [reddit_financialaid] JSON API error: {e}")
        return None

    posts = data.get("data", {}).get("children", [])
    kept = [
        p["data"] for p in posts
        if p["data"].get("score", 0) >= 50
        and p["data"].get("num_comments", 0) >= 5
        and p["data"].get("selftext", "").strip()
    ]

    if not kept:
        print("  [reddit_financialaid] No qualifying posts found via API.")
        return None

    documents = []
    for post in kept[:5]:
        post_id = post["id"]
        title = post["title"]
        body = post["selftext"].strip()

        comments_url = f"https://old.reddit.com/r/financialaid/comments/{post_id}.json"
        try:
            cresp = requests.get(comments_url, headers=HEADERS, timeout=15)
            cresp.raise_for_status()
            cdata = cresp.json()
            comment_nodes = cdata[1]["data"]["children"]
            comments = []
            for node in comment_nodes:
                if node["kind"] == "t1":
                    text = node["data"].get("body", "").strip()
                    if text and text != "[deleted]" and text != "[removed]":
                        comments.append(text)
                if len(comments) >= 5:
                    break
        except Exception:
            comments = []

        parts = [f"POST TITLE: {title}", "", body]
        for c in comments:
            parts += ["", "---", "", c]
        documents.append("\n".join(parts))
        time.sleep(1)

    return "\n\n" + ("=" * 60) + "\n\n".join(documents)


def fetch_url(source: dict) -> str | None:
    """
    Fetch a source. Returns raw text (HTML or plain).
    Loads from disk if raw file already exists — skips network call.
    """
    raw_path = os.path.join(RAW_DIR, f"{source['filename']}.txt")

    if os.path.exists(raw_path) and os.path.getsize(raw_path) > 100:
        print(f"  [{source['name']}] Loading from disk (raw already saved)")
        with open(raw_path, "r", encoding="utf-8") as f:
            return f.read()

    if source["type"] == "reddit":
        print(f"  [{source['name']}] Fetching via Reddit JSON API...")
        result = fetch_reddit()
        if result is None:
            _print_manual_instructions(source)
        return result

    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=15)
        resp.raise_for_status()
        print(f"  [{source['name']}] Fetched OK ({len(resp.text):,} bytes)")
        time.sleep(1)
        return resp.text
    except requests.exceptions.HTTPError as e:
        print(f"  [{source['name']}] HTTP {e.response.status_code} — see manual instructions below")
    except requests.exceptions.ConnectionError:
        print(f"  [{source['name']}] Connection error")
    except requests.exceptions.Timeout:
        print(f"  [{source['name']}] Timed out after 15s")
    except Exception as e:
        print(f"  [{source['name']}] Error: {e}")

    _print_manual_instructions(source)
    return None


def _print_manual_instructions(source: dict) -> None:
    raw_path = os.path.join(RAW_DIR, f"{source['filename']}.txt")
    print(f"""
  ┌─ MANUAL COLLECTION NEEDED ────────────────────────────────
  │  Source : {source['name']}
  │  URL    : {source['url']}
  │  1. Open the URL in your browser
  │  2. Select all visible text (Cmd+A) and copy
  │  3. Paste into: {raw_path}
  │  4. Re-run: python pipeline.py
  └───────────────────────────────────────────────────────────
""")


# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------

REMOVE_TAGS = [
    "script", "style", "nav", "header", "footer", "aside",
    "form", "noscript", "iframe", "button", "svg", "figure",
]

REMOVE_SELECTORS = [
    "#cookie-banner", ".cookie", ".ad", ".advertisement", ".promo",
    ".newsletter", ".signup", ".social-share", ".breadcrumb",
    ".site-header", ".site-footer", ".sidebar", ".related-articles",
    "[aria-label='breadcrumb']", ".back-to-top", ".skip-nav",
    "#header", "#footer", "#sidebar",
]


def _find_main_content(soup: BeautifulSoup, source_type: str):
    """Return the best content container for the given source type."""
    if source_type == "government":
        return (
            soup.find("main")
            or soup.find("article")
            or soup.find(id="content")
            or soup.body
        )
    if source_type == "commercial":
        return (
            soup.find("article")
            or soup.find("main")
            or soup.find(class_=lambda c: c and any(w in " ".join(c).lower() for w in ["article", "content", "post"]))
            or soup.body
        )
    # nonprofit
    return (
        soup.find("main")
        or soup.find(class_=lambda c: c and any(w in " ".join(c).lower() for w in ["content", "page", "body", "entry"]))
        or soup.body
    )


def _normalize(text: str) -> str:
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [line.strip() for line in text.splitlines()]
    return '\n'.join(line for line in lines if line)


def clean_document(raw_text: str, source: dict) -> str:
    """Strip boilerplate from raw HTML and return plain text."""
    if source["type"] == "reddit":
        return _normalize(raw_text)

    # If the raw file is plain text (manually pasted), skip HTML parsing.
    if not raw_text.lstrip().startswith("<"):
        return _normalize(raw_text)

    soup = BeautifulSoup(raw_text, "html.parser")

    for tag in soup(REMOVE_TAGS):
        tag.decompose()

    for selector in REMOVE_SELECTORS:
        for el in soup.select(selector):
            el.decompose()

    container = _find_main_content(soup, source["type"])
    if container is None:
        return ""

    text = container.get_text(separator="\n", strip=True)
    text = _normalize(text)

    # Commercial pages embed loan-comparison ad widgets after the article.
    # Truncate at the first ad boundary to keep only the editorial content.
    if source["type"] == "commercial":
        for marker in ("Advertisement\n", "Student loans from our partners", "Advertiser Disclosure"):
            idx = text.find(marker)
            if idx > 500:
                text = text[:idx].rstrip()
                break

    return text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_ingest() -> list[dict]:
    """
    Fetch and clean all sources. Returns list of dicts:
      {"source": <source dict>, "clean_text": <str>}
    Skips sources where fetching or cleaning yields too little content.
    """
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(CLEAN_DIR, exist_ok=True)

    results = []

    print("\n" + "=" * 60)
    print("STAGE 1 — FETCH")
    print("=" * 60)

    for source in SOURCES:
        raw_text = fetch_url(source)
        if raw_text is None:
            continue
        raw_path = os.path.join(RAW_DIR, f"{source['filename']}.txt")
        if not (os.path.exists(raw_path) and os.path.getsize(raw_path) > 100):
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw_text)
        results.append({"source": source, "raw_text": raw_text})

    print(f"\n→ {len(results)}/{len(SOURCES)} sources fetched\n")

    print("=" * 60)
    print("STAGE 2 — CLEAN")
    print("=" * 60)

    cleaned = []
    for item in results:
        source = item["source"]
        raw = item["raw_text"]
        clean = clean_document(raw, source)

        raw_len = len(raw)
        clean_len = len(clean)
        ratio = (clean_len / raw_len * 100) if raw_len > 0 else 0
        status = "⚠ TOO SHORT" if clean_len < 300 else "OK"

        print(f"  [{source['name']}] {raw_len:,} → {clean_len:,} chars ({ratio:.1f}%)  {status}")

        if clean_len < 300:
            _print_manual_instructions(source)
            continue

        clean_path = os.path.join(CLEAN_DIR, f"{source['filename']}.txt")
        with open(clean_path, "w", encoding="utf-8") as f:
            f.write(clean)

        cleaned.append({"source": source, "clean_text": clean})

    print(f"\n→ {len(cleaned)} documents ready for chunking\n")
    return cleaned
