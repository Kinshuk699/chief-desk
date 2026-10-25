#!/usr/bin/env python3
"""Reach Indian official documents when the usual sites fail. Stdlib only.

  gov_sources.py sansad "oxygen high altitude" [--n 10]       Parliament e-library search (committee reports,
                                                               debates, papers): title, date, PDF url
  gov_sources.py sansad-text <item-uuid> [--grep oxygen]      download that item's PDF, print matching passages
  gov_sources.py wayback-find drdo.gov.in "oxygen|dipas"      list archived pages whose URL matches a regex
  gov_sources.py wayback-get <url>                            closest archived copy of a URL (use that URL as source,
                                                               and also cite the original)
  gov_sources.py papers "oxygen enrichment altitude" [--drdo] Crossref search (--drdo = DRDO journals only,
                                                               DOI prefix 10.14429; full text at publicationsdrdo.in)

Routes and why they exist: ~/ChiefDesk/ACCESS_ROUTES.md. Polite by design: one request at a time, pauses and
retries on HTTP 429, never tries to get past a CAPTCHA or login.
"""
import json, re, sys, time, urllib.error, urllib.parse, urllib.request, os, tempfile

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
EL = "https://elibrary.sansad.in/server/api"

def get(url, binary=False, tries=4, timeout=40):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                wait = 10 * (i + 1); print(f"[429] pausing {wait}s", file=sys.stderr); time.sleep(wait); continue
            raise
        except Exception:
            if i < tries - 1: time.sleep(3); continue
            raise

def md(meta, key):
    v = meta.get(key) or [{}]
    return v[0].get("value", "")

def sansad(query, n=10):
    q = urllib.parse.quote(query)
    d = json.loads(get(f"{EL}/discover/search/objects?query={q}&size={n}"))
    sr = d["_embedded"]["searchResult"]
    print(f"{sr['page']['totalElements']} hits for {query!r} (showing {len(sr['_embedded']['objects'])})")
    for o in sr["_embedded"]["objects"]:
        it = o["_embedded"]["indexableObject"]; m = it.get("metadata", {})
        print(f"- {md(m,'dc.date.issued')[:10]} | {md(m,'dc.title')[:140]}\n  uuid {it['uuid']}  page https://elibrary.sansad.in/items/{it['uuid']}")

def pdf_url(uuid):
    b = json.loads(get(f"{EL}/core/items/{uuid}/bundles"))
    for bundle in b["_embedded"]["bundles"]:
        if bundle["name"] == "ORIGINAL":
            bs = json.loads(get(bundle["_links"]["bitstreams"]["href"]))
            for s in bs["_embedded"]["bitstreams"]:
                return s["_links"]["content"]["href"], s["name"]
    return None, None

def sansad_text(uuid, pattern="oxygen", width=350):
    url, name = pdf_url(uuid)
    if not url: print("no PDF on this item"); return
    print(f"PDF: {url}  ({name})")
    data = get(url, binary=True, timeout=120)
    path = os.path.join(tempfile.gettempdir(), f"sansad-{uuid}.pdf"); open(path, "wb").write(data)
    try:
        import fitz  # pymupdf
        doc = fitz.open(path); pages = [p.get_text() for p in doc]
    except ImportError:
        print(f"pymupdf not installed; PDF saved at {path}"); return
    hits = 0
    for i, t in enumerate(pages):
        for m in re.finditer(pattern, t, re.I):
            s = " ".join(t[max(0, m.start() - width): m.end() + width].split())
            print(f"\n[page {i+1}] …{s}…"); hits += 1
            if hits >= 25: print("\n(25 passages shown; narrow --grep)"); return
    print(f"\n{hits} passages matched /{pattern}/ in {len(pages)} pages. Saved: {path}")

def wayback_find(domain, regex, limit=25):
    u = (f"http://web.archive.org/cdx/search/cdx?url={urllib.parse.quote(domain)}/*"
         f"&filter=original:.*({urllib.parse.quote(regex)}).*&filter=statuscode:200&collapse=urlkey&limit={limit}"
         f"&fl=timestamp,original")
    for line in get(u).splitlines():
        ts, orig = line.split(" ", 1)
        print(f"{ts[:8]}  https://web.archive.org/web/{ts}/{orig}")

def wayback_get(url):
    d = json.loads(get("http://archive.org/wayback/available?url=" + urllib.parse.quote(url)))
    s = d.get("archived_snapshots", {}).get("closest")
    print(f"{s['timestamp'][:8]}  {s['url']}" if s else "no archived copy")

def papers(query, drdo=False, n=10):
    f = "&filter=prefix:10.14429" if drdo else ""
    d = json.loads(get(f"https://api.crossref.org/works?query={urllib.parse.quote(query)}{f}&rows={n}"
                       "&select=title,DOI,container-title,issued,author"))["message"]
    print(f"{d['total-results']} results")
    for w in d["items"]:
        y = (w.get("issued", {}).get("date-parts") or [[None]])[0][0]
        au = ", ".join(a.get("family", "") for a in (w.get("author") or [])[:3])
        print(f"- {y} | {(w.get('title') or [''])[0][:110]} | {au} | {(w.get('container-title') or [''])[0]} | https://doi.org/{w['DOI']}")

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(0)
    def opt(name, default):
        if name in a: i = a.index(name); v = a[i + 1]; del a[i:i + 2]; return v
        return default
    cmd = a[0]
    if cmd == "sansad": n = int(opt("--n", 10)); sansad(" ".join(a[1:]), n)
    elif cmd == "sansad-text": g = opt("--grep", "oxygen"); sansad_text(a[1], g)
    elif cmd == "wayback-find": wayback_find(a[1], a[2])
    elif cmd == "wayback-get": wayback_get(a[1])
    elif cmd == "papers":
        drdo = "--drdo" in a; a = [x for x in a if x != "--drdo"]; papers(" ".join(a[1:]), drdo)
    else: print(__doc__)
