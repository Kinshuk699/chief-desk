#!/usr/bin/env bash
# install.sh: set up ChiefDesk on a machine with Hermes installed.
# Needs DEEPSEEK_API_KEY, GLM_API_KEY, FIRECRAWL_API_KEY, TYPESAFE_API_KEY in ~/.hermes/.env first.
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"; H="$HOME/.hermes"
mkdir -p "$H/skills/autonomous-ai-agents" "$H/skills/personal"
cp -R "$R/skills/chief-desk" "$R/skills/jev-judge" "$H/skills/autonomous-ai-agents/"
cp -R "$R/skills/kinshuk-context" "$H/skills/personal/"
[ "$R" != "$HOME/ChiefDesk" ] && { mkdir -p "$HOME/ChiefDesk"; rsync -a --exclude .git "$R/" "$HOME/ChiefDesk/"; }
for p in researcher skeptic maker writer; do
  if [ ! -d "$H/profiles/$p" ]; then
    model=$(python3 -c "import re,sys;print(re.search(r'default:\s*(\S+)',open('$R/profiles/$p/config.yaml').read()).group(1))")
    prov=deepseek; [ "$p" = skeptic ] && prov=zai
    "$R/bin/mint-profile.sh" "$p" "$prov" "$model" "ChiefDesk $p"
  fi
  cp "$R/profiles/$p/SOUL.md" "$H/profiles/$p/SOUL.md"
done
hermes kanban boards create desk 2>/dev/null || true
echo "ChiefDesk installed. In any Hermes chat (default profile): 'use the chief-desk skill'."
