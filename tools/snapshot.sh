#!/usr/bin/env bash
# Save the files you added to ledgerly/ (CLAUDE.md, CLAUDE.local.md, .claude/rules, nested
# CLAUDE.md files...) as a named variant you can re-run with run_drill.sh.
#
#   tools/snapshot.sh mine            -> my-variants/mine/
#   tools/run_drill.sh led-105 mine 3
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/ledgerly"
NAME="${1:?usage: snapshot.sh <variant-name>}"
DEST="$ROOT/my-variants/$NAME"
rm -rf "$DEST" && mkdir -p "$DEST"
count=0
while IFS= read -r f; do
  case "$f" in
    *.md|.claude/*|.mcp.json) mkdir -p "$DEST/$(dirname "$f")"; cp "$APP/$f" "$DEST/$f"; count=$((count+1)); echo "  + $f";;
  esac
done < <(git -C "$APP" ls-files --others --exclude-standard)
if [ -f "$APP/CLAUDE.local.md" ]; then cp "$APP/CLAUDE.local.md" "$DEST/"; count=$((count+1)); echo "  + CLAUDE.local.md"; fi
echo "saved $count file(s) to my-variants/$NAME"
