#!/usr/bin/env python3
"""Firecrawl credit check + swap to a backup key. Never prints key values.

  firecrawl_credits.py                  show remaining credits for the active key and the backup key
  firecrawl_credits.py --swap-below 25  if the active key has < 25 credits left and the backup has more,
                                        make the backup the active key in every .env that uses Firecrawl

Setup (Kinshuk does this himself, never via chat): add a line to ~/.hermes/.env
  FIRECRAWL_API_KEY_2=<second key>
On swap, the old active key is kept as FIRECRAWL_API_KEY_OLD in each file (.env.bak-<time> backups too).
Running worker processes keep the key they started with; new cards pick up the swapped key.
"""
import json, os, re, shutil, sys, time, urllib.request

HOME = os.path.expanduser("~/.hermes")
ENV_FILES = [os.path.join(HOME, ".env")] + [
    os.path.join(HOME, "profiles", p, ".env") for p in ("researcher", "skeptic", "maker", "writer")]

def read_env(path):
    vals = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            m = re.match(r"\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$", line)
            if m: vals[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return vals

def mask(k): return f"…{k[-4:]}" if k else "(none)"

def credits(key):
    if not key: return None
    req = urllib.request.Request("https://api.firecrawl.dev/v1/team/credit-usage",
                                 headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)["data"].get("remaining_credits")
    except Exception as e:
        return f"error: {str(e)[:60]}"

def set_key(path, new_value, old_value):
    text = open(path, encoding="utf-8").read()
    shutil.copy2(path, f"{path}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    text = re.sub(r"(?m)^\s*FIRECRAWL_API_KEY_OLD\s*=.*\n?", "", text)
    text = re.sub(r"(?m)^(\s*FIRECRAWL_API_KEY\s*=).*$", lambda m: m.group(1) + new_value, text)
    text = text.rstrip("\n") + f"\nFIRECRAWL_API_KEY_OLD={old_value}\n"
    open(path, "w", encoding="utf-8").write(text)

def main():
    main_env = read_env(ENV_FILES[0])
    active, backup = main_env.get("FIRECRAWL_API_KEY", ""), main_env.get("FIRECRAWL_API_KEY_2", "")
    users = [p for p in ENV_FILES if read_env(p).get("FIRECRAWL_API_KEY")]
    ca, cb = credits(active), credits(backup)
    print(f"active key {mask(active)}: {ca} credits left")
    print(f"backup key {mask(backup)}: {cb if backup else 'not set (add FIRECRAWL_API_KEY_2 to ~/.hermes/.env)'}")
    for p in users:
        k = read_env(p).get("FIRECRAWL_API_KEY")
        print(f"  {p.replace(HOME, '~/.hermes')}: uses {mask(k)}{'' if k == active else '  (differs from main .env)'}")
    if "--swap-below" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--swap-below") + 1])
        if not backup:
            print("no swap: backup key not set"); return
        if not isinstance(ca, int) or not isinstance(cb, int):
            print("no swap: couldn't read credits for both keys"); return
        if ca >= limit:
            print(f"no swap: active key still has {ca} (>= {limit})"); return
        if cb <= ca:
            print("no swap: backup doesn't have more credits"); return
        for p in users:
            set_key(p, backup, read_env(p).get("FIRECRAWL_API_KEY", ""))
        print(f"SWAPPED: {len(users)} .env files now use {mask(backup)}; old key kept as FIRECRAWL_API_KEY_OLD")

if __name__ == "__main__":
    main()
