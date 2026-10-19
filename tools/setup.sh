#!/usr/bin/env bash
# Turn ledgerly/ into a local git repo with a `baseline` tag. Runs automatically the first time
# any tool is used after a fresh clone; safe to run again (it does nothing if the repo exists).
#
#   tools/setup.sh
#
# Why: ledgerly/ is tracked as plain files in the workshop repo (so it's on GitHub), but the agent
# must see ledgerly/ as its own project root. With a local .git inside it, `git status`,
# `git ls-files` and `git log` from inside ledgerly/ show only the app, never exercises/, and
# tools/reset.sh and the drift checker diff against the `baseline` tag.
#
# Bash 3.2 compatible (macOS default).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/ledgerly"

if [ -e "$APP/.git" ]; then
  if git -C "$APP" rev-parse -q --verify refs/tags/baseline >/dev/null; then
    exit 0
  fi
  echo "ledgerly/.git exists but has no 'baseline' tag. Fix it by hand or remove ledgerly/.git and re-run." >&2
  exit 1
fi

# The baseline must be the app exactly as the workshop repo ships it. Refuse if it's been edited.
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1 &&
   [ -n "$(git -C "$ROOT" status --porcelain -- ledgerly)" ]; then
  echo "ledgerly/ has local changes in the workshop repo. Restore it first:" >&2
  echo "  git checkout -- ledgerly && git clean -fd ledgerly" >&2
  exit 1
fi

echo "setting up ledgerly/ as a local repo with tag 'baseline'…"
G=(git -C "$APP" -c user.name="Ledgerly workshop" -c user.email="workshop@ledgerly.invalid" -c commit.gpgsign=false)
"${G[@]}" init -q -b main 2>/dev/null || "${G[@]}" init -q
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1 && [ -n "$(git -C "$ROOT" ls-files -- ledgerly | head -1)" ]; then
  # exactly the files the workshop repo tracks: your own CLAUDE.md etc. never become "baseline"
  (cd "$ROOT" && git ls-files -z -- ledgerly) | while IFS= read -r -d '' f; do
    "${G[@]}" add -- "${f#ledgerly/}"
  done
else
  "${G[@]}" add -A   # downloaded as a zip: no workshop repo to ask
fi
"${G[@]}" commit -q -m "Ledgerly 0.4.2 — workshop baseline"
"${G[@]}" tag baseline
echo "ledgerly/ ready: $(git -C "$APP" ls-files | wc -l | tr -d ' ') files at tag 'baseline'"
