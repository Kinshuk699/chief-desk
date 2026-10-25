#!/usr/bin/env bash
# mint-profile.sh <name> <provider> <model> "<description>"
#
# Creates a general-desk worker profile the same way every time:
#   - blank profile (bundled skills only; no NSE config, quick_commands or personalities)
#   - least-privilege .env: model + web keys and runtime settings ONLY
#     (never broker credentials, data-vendor tokens or messaging bot tokens)
#   - model pinned, cwd = ~/ChiefDesk, Chief's skills exposed read-through
# Afterwards: write ~/.hermes/profiles/<name>/SOUL.md and add a row to ~/ChiefDesk/ROSTER.md.
set -euo pipefail

if [ $# -ne 4 ]; then
  echo "usage: $0 <name> <provider> <model> \"<description>\"" >&2
  exit 2
fi
name=$1 provider=$2 model=$3 desc=$4
home="$HOME/.hermes/profiles/$name"

case "$name" in
  builder|designer|fund-analyst|guardian|orchestrator|scout|tech-analyst|verifier|default)
    echo "refusing: '$name' is reserved (NSE stock desk / default)" >&2; exit 1;;
esac
[ -e "$home" ] && { echo "refusing: profile '$name' already exists" >&2; exit 1; }

hermes profile create "$name" --description "$desc" >/dev/null

python3 - "$home" <<'EOF'
import os, re, sys
src = os.path.expanduser('~/.hermes/.env')
dst = os.path.join(sys.argv[1], '.env')
allow = re.compile(
    r'^(DEEPSEEK_API_KEY|GLM_API_KEY|FIRECRAWL_API_KEY|JINA_API_KEY|TYPESAFE_API_KEY'
    r'|BROWSER_[A-Z_]+|BROWSERBASE_(ADVANCED_STEALTH|PROXIES)|TERMINAL_[A-Z_]+)=')
keep = [l.strip() for l in open(src).read().split('\n') if allow.match(l.strip())]
old = open(dst).read() if os.path.exists(dst) else ''
with open(dst, 'w') as f:
    if old.strip():
        f.write(old.rstrip('\n') + '\n')
    f.write('\n'.join(keep) + '\n')
os.chmod(dst, 0o600)
names = sorted({l.split('=', 1)[0] for l in keep})
print(f"env: {len(names)} keys -> {', '.join(names)}")
EOF

H="hermes -p $name config set"
$H model.provider "$provider" >/dev/null
$H model.default "$model" >/dev/null
$H model.base_url '' >/dev/null
$H terminal.cwd "$HOME/ChiefDesk" >/dev/null
$H skills.external_dirs "[\"$HOME/.hermes/skills\"]" >/dev/null
echo "minted $name ($provider/$model) at $home"
