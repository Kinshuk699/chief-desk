#!/usr/bin/env python3
"""jev_check.py: cheap Jev (TypeSafe System One) judgments for the Chief desk.

Modes
  claims  JSONL rows {id, claim, quote?, passage?, source_file?, source_url?}
          -> does the passage (or the quote's context in the source) support the claim?
  prose   --file draft.md, or JSONL rows {id, text}
          -> AI-tell flags per paragraph (code checks + Jev nouls + a genericness score)
  raw     JSONL rows {id, state, questions}  -> raw Jev answers for custom questions
  models  list the model names this key can use

Stdlib only (Python 3.9+). Key: $TYPESAFE_API_KEY, else $HERMES_HOME/.env, else ~/.hermes/.env.
Everything in `state` goes to TypeSafe's US servers: send public text and drafts meant for
publication only. No credentials, no non-public personal data.

Questions and thresholds live in the CONSTANTS block below (TypeSafe's own advice: keep
them in one place so a human can review them). Thresholds are calibrated in
references/calibration.md; change a question's wording and you must recalibrate.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import html.parser
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

# ============================== CONSTANTS ==============================
MODEL = "jev-1.14.0"  # pinned; the alias jev-latest moved 1.13.0 -> 1.14.0 in Oct 2026
ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODELS_ENDPOINT = "https://api.typesafe.ai/v1/models"
PRICE_PER_M_INPUT = 0.042  # USD; output tokens are free (vendor pricing, Oct 2026)
USER_AGENT = "jev-judge/0.1 (Chief desk verification script)"

# ---- claims ----
CLAIM_QUESTION = {
    "type": "choice",
    "instructions": (
        "How does the passage relate to the claim? Judge only from what the passage says, "
        "not from outside knowledge."
    ),
    "criteria": {
        "supports": (
            "The passage states the whole claim or directly implies every part of it, "
            "including any numbers, names, dates and versions in the claim"
        ),
        "contradicts": (
            "The passage states something that makes the claim false, such as a different "
            "number, name, date or version, or the opposite of the claim"
        ),
        "says_nothing": (
            "The passage does not address the claim, or it supports only part of the claim "
            "and is silent on the rest"
        ),
    },
}
CLAIM_AUTO = 0.80        # confidence >= this: the verdict stands; below: a reviewer looks
CONTEXT_CHARS = 1500     # chars of source context on each side of a located quote
MAX_PASSAGE_CHARS = 60000  # whole-source fallback cap (~15K tokens; limit is 32K/question)

# ---- prose ----
PROSE_NOULS = {
    "not_x_but_y": (
        "The paragraph uses a negative-parallel contrast for rhetorical effect, such as "
        "\"it's not X, it's Y\", \"not just X but Y\", \"not only X but also Y\", "
        "\"X, not Y\" or \"the reason was not X, it was Y\""
    ),
    "triplet": (
        "The paragraph contains a list of exactly three parallel items (three adjectives, "
        "three verbs, three nouns or three clauses) used for rhythm or emphasis"
    ),
    "hedge": (
        "The paragraph stacks hedges and qualifiers, such as \"could potentially\", "
        "\"might possibly\", \"it could be argued\", \"arguably\", \"somewhat\", \"perhaps\""
    ),
    "kicker": (
        "The paragraph ends on a short slogan-like or quotable line, a generic upbeat "
        "conclusion, a moral, or a reassurance line, written for effect rather than information"
    ),
    "inflated": (
        "The paragraph inflates significance or sounds promotional, with words like "
        "\"pivotal\", \"testament\", \"transformative\", \"groundbreaking\", \"seamless\", "
        "\"plays a crucial role\" or \"evolving landscape\""
    ),
}
PROSE_GENERIC = {
    "type": "score",
    "instructions": (
        "How generic the paragraph reads: could it have been written by an AI assistant about "
        "anyone, or does it sound like a specific person describing specific things?"
    ),
    "criteria": [
        "Specific and personal: concrete details, a particular voice, uneven natural rhythm",
        "Mostly specific, with a stock phrase or two",
        "Generic: smooth, evenly paced, interchangeable phrasing with few concrete details",
        "Boilerplate assistant prose: stock phrases, balanced structures, no concrete details",
    ],
}
NOUL_FLAG = {k: 0.50 for k in PROSE_NOULS}  # p(yes) >= this flags the tell
NOUL_FLAG["kicker"] = 0.70  # calibration: a promotional one-sentence paragraph scored 0.67 without a kicker
GENERIC_FLAG = 1.50   # score position on 0..3 at/above which a paragraph is flagged generic
MIN_PARAGRAPH_WORDS = 8

# Code checks (deterministic, no model needed)
EM_DASH = re.compile(r"\u2014| -- ")
AI_VOCAB = re.compile(
    r"\b(delve|delves|delving|tapestry|testament|pivotal|underscores?|underscoring|"
    r"showcas(?:e|es|ing)|fostering|intricate|interplay|vibrant|seamless(?:ly)?|"
    r"groundbreaking|transformative|game[- ]changer|evolving landscape|in today's|"
    r"at its core|let's dive|deep dive|navigate the|unlock(?:ing)? the|"
    r"it's important to note|in conclusion|plays? a (?:crucial|vital|key) role)\b",
    re.I,
)
STACCATO_MAX_WORDS = 3

# Pages that are a bot check, not the article (checked in the first 6 KB of HTML)
BOT_CHECK_MARKERS = ("recaptcha/challengepage", "recaptchachallengepageui", "cf-chl-", "challenge-platform",
                     "<title>just a moment", "<title>attention required", "<title>access denied",
                     "are you a robot", "verify you are human")
MIN_PAGE_CHARS = 1500  # fetched text shorter than this is treated as "no article body"

SECRET = re.compile(
    r"(sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|"
    r"Bearer\s+[A-Za-z0-9._-]{20,}|(?i:api[_-]?key|secret|password)\s*[:=]\s*\S{8,})"
)
# ======================================================================


def load_key() -> str:
    key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if key:
        return key
    homes = [os.environ.get("HERMES_HOME", ""), os.path.expanduser("~/.hermes")]
    for home in homes:
        path = os.path.join(home, ".env") if home else ""
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("TYPESAFE_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("jev_check: TYPESAFE_API_KEY not found in env, $HERMES_HOME/.env or ~/.hermes/.env")


class Usage:
    def __init__(self):
        self.lock = threading.Lock()
        self.calls = 0
        self.input_tokens = 0

    def add(self, tokens: int):
        with self.lock:
            self.calls += 1
            self.input_tokens += tokens


USAGE = Usage()


def call_jev(key: str, state, questions: dict, model: str, dry_run: bool = False) -> dict:
    """POST one System One request. Returns the parsed response (answers keyed by name)."""
    blob = json.dumps(state, ensure_ascii=False)
    if SECRET.search(blob):
        raise ValueError("BLOCKED: state looks like it contains a credential; not sent")
    body = {"model": model, "state": state, "questions": questions}
    if dry_run:
        return {"dry_run": True, "request": body}
    data = json.dumps(body).encode()
    delay = 1.0
    for attempt in range(5):
        req = urllib.request.Request(
            ENDPOINT,
            data=data,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                out = json.loads(resp.read().decode())
            USAGE.add(int(out.get("usage", {}).get("input_tokens") or 0))
            return out
        except urllib.error.HTTPError as err:
            text = err.read().decode(errors="replace")[:400]
            if err.code == 429 or err.code >= 500:
                retry_after = err.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else delay)
                delay *= 2
                continue
            raise RuntimeError(f"HTTP {err.code}: {text}") from None
        except (urllib.error.URLError, TimeoutError) as err:
            time.sleep(delay)
            delay *= 2
            last = err
            continue
    raise RuntimeError("Jev request failed after 5 attempts (rate limit or network)")


# ------------------------------ sources ------------------------------
class _Text(html.parser.HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "head"}
    BLOCK = {"p", "div", "li", "tr", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "br",
             "section", "article", "pre", "table", "blockquote"}

    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_to_text(raw: str) -> str:
    parser = _Text()
    parser.feed(raw)
    return re.sub(r"\n\s*\n+", "\n\n", "".join(parser.parts))


def read_source_file(path: str) -> str:
    with open(os.path.expanduser(path), encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    if path.lower().endswith((".html", ".htm")) or raw.lstrip()[:200].lower().startswith(("<!doctype", "<html")):
        return html_to_text(raw)
    return raw


_host_locks: dict = {}
_host_last: dict = {}
_glock = threading.Lock()


def _pdf_text(data: bytes) -> str:
    """Text of a PDF (needs pymupdf; without it, PDFs come back as FETCH_FAILED as before)."""
    try:
        import fitz  # pymupdf
    except ImportError:
        raise RuntimeError("FETCH_FAILED: PDF source; install pymupdf to read it") from None
    doc = fitz.open(stream=data, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def _sansad_pdf_url(url: str):
    """Parliament e-library item pages are a JavaScript app; resolve the item's PDF via its public API."""
    m = re.search(r"elibrary\.sansad\.in/items/([0-9a-f-]{36})", url)
    if not m:
        return None
    api = "https://elibrary.sansad.in/server/api/core/items/%s/bundles" % m.group(1)
    with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": USER_AGENT}), timeout=30) as r:
        bundles = json.load(r)["_embedded"]["bundles"]
    for b in bundles:
        if b["name"] == "ORIGINAL":
            with urllib.request.urlopen(urllib.request.Request(b["_links"]["bitstreams"]["href"],
                                        headers={"User-Agent": USER_AGENT}), timeout=30) as r:
                bs = json.load(r)["_embedded"]["bitstreams"]
            if bs:
                return bs[0]["_links"]["content"]["href"]
    return None


def fetch_url(url: str) -> str:
    """Polite GET: one request at a time per host, 1 s spacing, honours Retry-After.
    Reads HTML, plain text and PDFs (pymupdf); Parliament e-library items resolve to their PDF.
    No evasion of anything: blocked, login-walled or JS-only pages come back as errors."""
    try:
        alt = _sansad_pdf_url(url)
    except Exception:
        alt = None
    if alt:
        url = alt
    host = urllib.parse.urlparse(url).netloc
    with _glock:
        lock = _host_locks.setdefault(host, threading.Lock())
    with lock:
        delay = 2.0
        for attempt in range(3):
            wait = 1.0 - (time.time() - _host_last.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            _host_last[host] = time.time()
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    ctype = resp.headers.get("Content-Type", "")
                    data = resp.read()
                    charset = resp.headers.get_content_charset() or "utf-8"
                if "pdf" in ctype.lower() or data[:5] == b"%PDF-":
                    return _pdf_text(data)
                raw = data.decode(charset, errors="replace")
                head = raw[:6000].lower()
                if any(m in head for m in BOT_CHECK_MARKERS):
                    # A bot check / CAPTCHA page. Never try to get past it: report and move on.
                    raise RuntimeError("FETCH_BLOCKED: site served a bot check (CAPTCHA); open it with web tools or mark UNCHECKED")
                return html_to_text(raw) if "html" in ctype else raw
            except urllib.error.HTTPError as err:
                if err.code == 429 or err.code >= 500:
                    ra = err.headers.get("Retry-After")
                    time.sleep(float(ra) if ra and ra.isdigit() else delay)
                    delay *= 2
                    continue
                raise RuntimeError(f"FETCH_FAILED: HTTP {err.code}") from None
            except (urllib.error.URLError, TimeoutError) as err:
                time.sleep(delay)
                delay *= 2
        raise RuntimeError("FETCH_FAILED: rate-limited or unreachable after 3 tries")


# --------------------------- quote locating ---------------------------
_FOLD = str.maketrans({"\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'", "\u2014": "-",
                       "\u2013": "-", "\u00a0": " ", "\u2026": "..."})


def fold(text: str) -> str:
    text = text.replace("\\n", " ").translate(_FOLD)
    text = re.sub(r"[*_`|>#]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _find_one(low: str, q: str):
    """Locate one folded+lowercased fragment in `low`. Returns (kind, start, end) or None."""
    if not q:
        return None
    i = low.find(q)
    if i >= 0:
        return ("exact", i, i + len(q))
    frags = [f.strip(" .") for f in q.split("...") if len(f.split()) >= 3]
    if len(frags) > 1:
        pos, first = 0, None
        for frag in frags:
            j = low.find(frag, pos)
            if j < 0:
                break
            first = j if first is None else first
            pos = j + len(frag)
        else:
            return ("elided", first, pos)
    toks = re.findall(r"\w+", q)
    if len(toks) >= 8:
        n = 5
        shingles = [" ".join(toks[k:k + n]) for k in range(len(toks) - n + 1)]
        stoks = re.findall(r"\w+", low)
        sset = {" ".join(stoks[k:k + n]) for k in range(len(stoks) - n + 1)}
        hit = [s for s in shingles if s in sset]
        if len(hit) / len(shingles) >= 0.8:
            anchor = low.find(hit[0])
            if anchor < 0:
                anchor = max(low.find(hit[0].split()[0]), 0)
            return ("fuzzy", anchor, anchor + len(q))
    return None


def split_fragments(q: str):
    """Split a researcher quote like '"part one" ; "part two"' into its quoted parts."""
    parts = re.split(r'"\s*[;,/]?\s*(?:and\s+)?"', q)
    return [p.strip(" \"'.;,") for p in parts if p.strip(" \"'.;,")]


def locate_quote(source: str, quote: str):
    """Return (match_kind, [(start, end), ...]) in fold(source), or None. Tolerates whitespace,
    curly quotes, markdown marks, case, wrapping quote marks, several quoted parts joined by
    ';' (each part must be on the page), '...' elisions, and light rewording (>=80% of 5-word
    shingles)."""
    low = fold(source).lower()
    q = fold(quote).lower()
    if not q:
        return None
    hit = _find_one(low, q.strip(" \"'"))
    if hit:
        return (hit[0], [(hit[1], hit[2])])
    frags = [f for f in split_fragments(q) if len(f.split()) >= 3]
    if len(frags) > 1:
        spans, kinds = [], set()
        for frag in frags:
            h = _find_one(low, frag)
            if h is None:
                break
            kinds.add(h[0])
            spans.append((h[1], h[2]))
        else:
            return ("multi-exact" if kinds == {"exact"} else "multi-mixed", spans)
    # Fallback: loose match over the whole quote with quote marks and separators removed
    flat = re.sub(r"\s+", " ", re.sub(r"[\"';]+", " ", q)).strip()
    h = _find_one(low, flat)
    if h:
        return ("fuzzy" if h[0] != "exact" else "exact", [(h[1], h[2])])
    return None


# ------------------------------- claims -------------------------------
def judge_claim(row: dict, key: str, model: str, sources: dict, dry_run: bool) -> dict:
    out = {"id": row.get("id"), "claim": row.get("claim", "")}
    claim = (row.get("claim") or "").strip()
    if not claim:
        return {**out, "verdict": "ERROR", "error": "row has no claim"}
    quote = (row.get("quote") or "").strip()
    passage = (row.get("passage") or "").strip()
    src_key = row.get("source_file") or row.get("source_url")
    match = None
    if src_key:
        source = sources.get(src_key)
        if isinstance(source, Exception):
            return {**out, "verdict": "UNCHECKED", "error": str(source), "action": "review"}
        if quote:
            match = locate_quote(source, quote)
            if match is None and len(fold(source)) < MIN_PAGE_CHARS:
                return {**out, "verdict": "UNCHECKED", "match": None, "action": "review",
                        "error": "page returned almost no text (JS-only or blocked); open it with web tools"}
            if match is None:
                return {**out, "verdict": "QUOTE_NOT_FOUND", "match": None, "action": "review",
                        "note": "quote not in fetched text: fabricated, reworded, or page needs JS"}
            src = fold(source)
            windows = sorted((max(0, a - CONTEXT_CHARS), b + CONTEXT_CHARS) for a, b in match[1])
            merged = [list(windows[0])]
            for a, b in windows[1:]:
                if a <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], b)
                else:
                    merged.append([a, b])
            passage = " ... ".join(src[a:b] for a, b in merged)
        else:
            passage = fold(source)[:MAX_PASSAGE_CHARS]
    elif quote and not passage:
        passage = quote
    if not passage:
        return {**out, "verdict": "ERROR", "error": "row needs quote, passage, source_file or source_url"}
    try:
        state = {"claim": claim, "passage": passage}
        src_label = row.get("source") or row.get("source_url") or (os.path.basename(row["source_file"]) if row.get("source_file") else None)
        if src_label:
            state["source"] = src_label  # tells Jev which product/page the passage is about
        resp = call_jev(key, state, {"relation": CLAIM_QUESTION}, model, dry_run)
    except Exception as err:  # noqa: BLE001 - report per row, keep going
        return {**out, "verdict": "ERROR", "error": str(err)}
    if dry_run:
        return {**out, **resp}
    ans = resp["answers"]["relation"]
    verdict = {"supports": "SUPPORTED", "contradicts": "CONTRADICTED", "says_nothing": "NOT_SUPPORTED"}[ans["choice"]]
    conf = float(ans["confidence"])
    return {
        **out,
        "verdict": verdict,
        "confidence": round(conf, 3),
        "probabilities": {k: round(float(v), 3) for k, v in ans["probabilities"].items()},
        "action": "auto" if conf >= CLAIM_AUTO else "review",
        "match": match[0] if match else ("given-passage" if not src_key else "whole-source"),
        "model": resp.get("model"),
    }


def run_claims(rows, key, model, workers, dry_run):
    sources = {}
    files = {r["source_file"] for r in rows if r.get("source_file")}
    urls = {r["source_url"] for r in rows if r.get("source_url") and not r.get("source_file")}
    for path in files:
        try:
            sources[path] = read_source_file(path)
        except Exception as err:  # noqa: BLE001
            sources[path] = RuntimeError(f"SOURCE_FILE_ERROR: {err}")
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futs = {pool.submit(fetch_url, u): u for u in urls}
        for fut in cf.as_completed(futs):
            u = futs[fut]
            try:
                sources[u] = fut.result()
            except Exception as err:  # noqa: BLE001
                sources[u] = err
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        return list(pool.map(lambda r: judge_claim(r, key, model, sources, dry_run), rows))


# -------------------------------- prose --------------------------------
def split_paragraphs(text: str):
    paras, buf, start, in_code = [], [], None, False
    lines = text.splitlines()
    for n, line in enumerate(lines + [""], start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # Skip headings, tables, rules, images, figure HTML and credit lines: captions are not prose
        if line.strip() == "" or line.lstrip().startswith(("#", "|", "---", "![", "<figure", "<img", "*Credit", "_Credit")) or re.match(r"\s*\[\d+\] ", line):
            if buf:
                para = " ".join(s.strip() for s in buf)
                if len(para.split()) >= MIN_PARAGRAPH_WORDS:
                    paras.append({"id": f"p{len(paras) + 1}", "line": start, "text": para})
            buf, start = [], None
            continue
        if not buf:
            start = n
        buf.append(line)
    return paras


def code_checks(text: str) -> dict:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    stacc = [s for s in sentences if len(re.findall(r"\w+", s)) <= STACCATO_MAX_WORDS]
    return {
        "em_dashes": len(EM_DASH.findall(text)),
        "ai_vocab": sorted({m.group(0).lower() for m in AI_VOCAB.finditer(text)}),
        "staccato": stacc,
    }


def judge_paragraph(row: dict, key: str, model: str, dry_run: bool) -> dict:
    text = (row.get("text") or "").strip()
    out = {"id": row.get("id"), "line": row.get("line"), "preview": text[:70]}
    checks = code_checks(text)
    questions = {k: {"type": "noul", "instructions": v} for k, v in PROSE_NOULS.items()}
    questions["generic"] = PROSE_GENERIC
    try:
        resp = call_jev(key, {"paragraph": text}, questions, model, dry_run)
    except Exception as err:  # noqa: BLE001
        return {**out, **checks, "flag": None, "error": str(err)}
    if dry_run:
        return {**out, **resp}
    ans = resp["answers"]
    nouls = {k: round(float(ans[k]["noul"]), 3) for k in PROSE_NOULS}
    generic = round(float(ans["generic"]["score"]), 2)
    reasons = [k for k, p in nouls.items() if p >= NOUL_FLAG[k]]
    if generic >= GENERIC_FLAG:
        reasons.append("generic")
    if checks["em_dashes"]:
        reasons.append("em_dash")
    if checks["ai_vocab"]:
        reasons.append("ai_vocab")
    if len(checks["staccato"]) >= 2:
        reasons.append("staccato")
    return {**out, "flag": bool(reasons), "reasons": reasons, "nouls": nouls, "generic": generic,
            **checks, "model": resp.get("model")}


def run_prose(rows, key, model, workers, dry_run):
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        return list(pool.map(lambda r: judge_paragraph(r, key, model, dry_run), rows))


# --------------------------------- raw ---------------------------------
def run_raw(rows, key, model, workers, dry_run):
    def one(row):
        try:
            resp = call_jev(key, row["state"], row["questions"], model, dry_run)
            return {"id": row.get("id"), **resp}
        except Exception as err:  # noqa: BLE001
            return {"id": row.get("id"), "error": str(err)}
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        return list(pool.map(one, rows))


# -------------------------------- output --------------------------------
def md_cell(s, n=90) -> str:
    s = re.sub(r"\s+", " ", str(s)).replace("|", "/")
    return s if len(s) <= n else s[: n - 1] + "…"


def table(mode: str, results) -> str:
    if mode == "claims":
        lines = ["| id | claim | quote match | Jev verdict | conf | action |", "|---|---|---|---|---|---|"]
        for r in results:
            lines.append(f"| {r.get('id')} | {md_cell(r.get('claim', ''))} | {r.get('match', '-')} | "
                         f"{r.get('verdict')} | {r.get('confidence', '-')} | {r.get('action', '-')} |")
    else:
        lines = ["| id | line | flag | reasons | generic | preview |", "|---|---|---|---|---|---|"]
        for r in results:
            lines.append(f"| {r.get('id')} | {r.get('line', '-')} | {'FLAG' if r.get('flag') else 'ok'} | "
                         f"{', '.join(r.get('reasons', [])) or '-'} | {r.get('generic', '-')} | {md_cell(r.get('preview', ''), 60)} |")
    return "\n".join(lines)


def read_rows(path: str | None):
    fh = open(path, encoding="utf-8") if path and path != "-" else sys.stdin
    rows = [json.loads(line) for line in fh if line.strip()]
    for k, r in enumerate(rows, start=1):
        r.setdefault("id", f"r{k}")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["claims", "prose", "raw", "models"])
    ap.add_argument("--in", dest="inp", help="JSONL input (default stdin)")
    ap.add_argument("--file", help="prose mode: a markdown/text draft to split into paragraphs")
    ap.add_argument("--out", help="write JSONL results here (default stdout)")
    ap.add_argument("--table", action="store_true", help="also print a markdown table to stdout")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true", help="build requests, send nothing")
    args = ap.parse_args(argv)

    key = "" if args.dry_run else load_key()
    if args.mode == "models":
        req = urllib.request.Request(MODELS_ENDPOINT, headers={"Authorization": f"Bearer {key}", "User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(json.dumps(json.loads(resp.read().decode()), indent=2))
        return 0

    if args.mode == "prose" and args.file:
        with open(os.path.expanduser(args.file), encoding="utf-8") as fh:
            rows = split_paragraphs(fh.read())
    else:
        rows = read_rows(args.inp)

    t0 = time.time()
    runner = {"claims": run_claims, "prose": run_prose, "raw": run_raw}[args.mode]
    results = runner(rows, key, args.model, args.workers, args.dry_run)

    out_fh = open(args.out, "w", encoding="utf-8") if args.out else None
    for r in results:
        line = json.dumps(r, ensure_ascii=False)
        if out_fh:
            out_fh.write(line + "\n")
        elif not args.table:
            print(line)
    if out_fh:
        out_fh.close()
    if args.table:
        print(table(args.mode, results))

    counts: dict = {}
    for r in results:
        label = "dry-run" if r.get("dry_run") else (r.get("verdict") or ("FLAG" if r.get("flag") else ("ok" if r.get("flag") is False else "error")))
        counts[label] = counts.get(label, 0) + 1
    cost = USAGE.input_tokens / 1e6 * PRICE_PER_M_INPUT
    print(f"jev_check: {len(results)} rows, {USAGE.calls} Jev calls, {USAGE.input_tokens} input tokens "
          f"(~${cost:.5f}), {time.time() - t0:.1f}s, {counts}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
