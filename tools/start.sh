#!/usr/bin/env bash
# Get ledgerly/ ready for a drill: undo the last agent's code, keep your memory files
# (CLAUDE.md, .claude/rules, .claude/skills…), then apply the drill's start state, if it has one.
#
#   tools/start.sh led-120      # LED-105 already implemented, ready to be reviewed
#   tools/start.sh led-105      # plain baseline code (same as reset --keep-memory)
set -euo pipefail
source "$(dirname "$0")/_lib.sh"
DRILL="$(resolve_drill "${1:?usage: start.sh <drill>}")"
"$ROOT/tools/reset.sh" --keep-memory
if [ -x "$DRILL/setup.sh" ]; then "$DRILL/setup.sh" "$APP"; fi
echo "ready: $(basename "$DRILL") · prompt: ${DRILL#$ROOT/}/prompt.md"
