#!/usr/bin/env bash
# sync-from-hermes.sh: copy the live desk setup from ~/.hermes into this repo (run before committing).
# Copies worker SOUL.md + config.yaml and the desk skills. Never copies .env, sessions, state or memories.
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"; H="$HOME/.hermes"
for p in researcher skeptic maker writer; do
  mkdir -p "$R/profiles/$p"
  cp "$H/profiles/$p/SOUL.md" "$R/profiles/$p/SOUL.md"
  cp "$H/profiles/$p/config.yaml" "$R/profiles/$p/config.yaml"
done
mkdir -p "$R/skills"
rsync -a --delete --exclude '__pycache__' --exclude '.DS_Store' "$H/skills/autonomous-ai-agents/chief-desk/" "$R/skills/chief-desk/"
rsync -a --delete --exclude '__pycache__' --exclude '.DS_Store' "$H/skills/autonomous-ai-agents/jev-judge/" "$R/skills/jev-judge/"
rsync -a --delete --exclude '.DS_Store' "$H/skills/personal/kinshuk-context/" "$R/skills/kinshuk-context/"
# public-repo scrub: salary line stays local only
sed -i '' '/Comp ask:/d' "$R/skills/kinshuk-context/references/career.md"
# secret scan: abort if anything key-like slipped in
if grep -rInE '(sk-[A-Za-z0-9]{16,}|fc-[0-9a-f]{20,}|[A-Za-z0-9_]*(API_KEY|TOKEN|SECRET)=[^ $"]{8,}|ghp_[A-Za-z0-9]{20,})' "$R" --exclude-dir=.git --exclude-dir=projects --exclude-dir=explainers; then
  echo "SECRET-LIKE STRING FOUND: fix before committing" >&2; exit 1; fi
echo "synced into $R"
