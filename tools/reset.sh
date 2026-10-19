#!/usr/bin/env bash
# Put ledgerly/ back to the `baseline` tag.
#
#   tools/reset.sh                 # everything back to baseline: your CLAUDE.md files are removed too
#   tools/reset.sh --keep-memory   # undo the agent's code changes, keep your memory files
#                                  # (CLAUDE.md, CLAUDE.local.md, nested CLAUDE.md, .claude/, docs/standards/)
#
# Ignored files (.venv, .claude/settings.local.json for the load observer) are always kept.
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

KEEP=""
if [ "${1:-}" = "--keep-memory" ]; then
  KEEP="$(mktemp -d)"
  while IFS= read -r f; do
    case "$f" in
      CLAUDE.md|*/CLAUDE.md|.claude/*|.mcp.json|docs/standards/*)
        mkdir -p "$KEEP/$(dirname "$f")"; cp "$APP/$f" "$KEEP/$f";;
    esac
  done < <(git -C "$APP" ls-files --others --exclude-standard)
  [ -f "$APP/CLAUDE.local.md" ] && cp "$APP/CLAUDE.local.md" "$KEEP/"
fi

git -C "$APP" reset -q --hard baseline
git -C "$APP" clean -fdq
rm -f "$APP/CLAUDE.local.md"   # git-ignored on purpose, but must not leak between runs

if [ -n "$KEEP" ]; then
  (cd "$KEEP" && find . -type f -print) | while IFS= read -r f; do
    mkdir -p "$APP/$(dirname "$f")"; cp "$KEEP/$f" "$APP/$f"; echo "  kept ${f#./}"
  done
  rm -rf "$KEEP"
  echo "ledgerly/ code reset to baseline, memory files kept"
else
  echo "ledgerly/ reset to baseline"
fi
