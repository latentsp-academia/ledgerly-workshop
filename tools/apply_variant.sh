#!/usr/bin/env bash
# Copy a set of memory files (CLAUDE.md, .claude/rules, nested CLAUDE.md…) into ledgerly/.
#
#   tools/apply_variant.sh exercises/ex01-claude-md/reference     # any folder mirroring ledgerly/
#   tools/apply_variant.sh mine                                    # my-variants/mine (tools/snapshot.sh)
set -euo pipefail
source "$(dirname "$0")/_lib.sh"
V="${1:?usage: apply_variant.sh <folder | my-variants name>}"
if [ -d "$V" ]; then SRC="$(cd "$V" && pwd)"
elif [ -d "$ROOT/my-variants/$V" ]; then SRC="$ROOT/my-variants/$V"
else echo "no folder '$V' and no my-variants/$V" >&2; exit 1; fi
(cd "$SRC" && find . -type f ! -name '.keep' ! -name 'NOTES.md' ! -name '*.example' -print0) |
while IFS= read -r -d '' f; do
  mkdir -p "$APP/$(dirname "$f")"
  cp "$SRC/$f" "$APP/$f"
  echo "  applied ${f#./}"
done
