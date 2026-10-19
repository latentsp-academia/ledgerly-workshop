#!/usr/bin/env bash
# Run a drill headless N times against one set of memory files, then print pass rates.
#
#   tools/run_drill.sh led-105 none 3                                   # no CLAUDE.md at all
#   tools/run_drill.sh led-105 current 3                                # whatever you've written in ledgerly/
#   tools/run_drill.sh led-105 exercises/ex01-claude-md/reference 3     # the reference implementation
#
# Each run: reset ledgerly/ -> apply the files -> claude -p <prompt.md> -> drift check.
# Env: MODEL=<model id>  MAX_TURNS=40
set -euo pipefail
source "$(dirname "$0")/_lib.sh"
DRILL="$(resolve_drill "${1:?usage: run_drill.sh <drill> <none|current|folder|my-variant> [runs]}")"
VARIANT="${2:-none}"
RUNS="${3:-3}"
NAME="$(basename "$DRILL")"
LABEL="$(basename "$VARIANT")"
OUT="$ROOT/runs/$NAME/$LABEL"
mkdir -p "$OUT"

SRC=""
if [ "$VARIANT" = "current" ]; then
  # freeze what the student has written so every run starts from the same files
  SRC="$OUT/_files"; rm -rf "$SRC"; mkdir -p "$SRC"
  while IFS= read -r f; do
    case "$f" in *.md|.claude/*|.mcp.json) mkdir -p "$SRC/$(dirname "$f")"; cp "$APP/$f" "$SRC/$f";; esac
  done < <(git -C "$APP" ls-files --others --exclude-standard)
  [ -f "$APP/CLAUDE.local.md" ] && cp "$APP/CLAUDE.local.md" "$SRC/"
  echo "frozen your current memory files into runs/$NAME/current/_files"
elif [ "$VARIANT" != "none" ]; then
  SRC="$(resolve_variant "$DRILL" "$VARIANT")"
fi

USER_MD="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/CLAUDE.md"
if [ -s "$USER_MD" ]; then
  echo "⚠️  $USER_MD exists and is loaded into every run (that's Step 6 of Exercise 1)."
  echo "    For a clean experiment: mv \"$USER_MD\" \"$USER_MD.bak\"  (and move it back after)."
fi

# The agent may edit files and run project commands. Everything else is denied.
ALLOWED=(
  "Read" "Edit" "Write" "Glob" "Grep"
  "Bash(uv run:*)" "Bash(uv sync:*)" "Bash(make:*)" "Bash(python:*)" "Bash(python3:*)"
  "Bash(git status:*)" "Bash(git diff:*)" "Bash(git log:*)" "Bash(ls:*)" "Bash(cat:*)"
)
EXTRA=()
[ -n "${MODEL:-}" ] && EXTRA+=(--model "$MODEL")

for i in $(seq 1 "$RUNS"); do
  echo; echo "──── $NAME / $LABEL / run $i of $RUNS"
  "$ROOT/tools/reset.sh" >/dev/null
  [ -n "$SRC" ] && "$ROOT/tools/apply_variant.sh" "$SRC" >/dev/null
  if [ -x "$DRILL/setup.sh" ]; then "$DRILL/setup.sh" "$APP" >/dev/null; fi
  T="$OUT/run-$i.jsonl"
  ( cd "$APP" && claude -p "$(cat "$DRILL/prompt.md")" \
      --output-format stream-json --verbose \
      --permission-mode acceptEdits \
      --max-turns "${MAX_TURNS:-40}" \
      ${EXTRA[@]+"${EXTRA[@]}"} \
      --allowedTools "${ALLOWED[@]}" ) > "$T" 2>"$OUT/run-$i.stderr" || true
  python3 "$ROOT/tools/drift_check.py" "$DRILL" --transcript "$T" --label "$LABEL" || true
done

python3 "$ROOT/tools/drift_check.py" --summary "$ROOT/runs/$NAME"
