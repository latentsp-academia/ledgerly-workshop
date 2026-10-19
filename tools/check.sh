#!/usr/bin/env bash
# Grade the current state of ledgerly/ (+ your newest Claude Code session) against a drill.
#
#   tools/check.sh led-105          # after you ran the LED-105 prompt interactively
#   tools/check.sh led-112 --label devB
set -euo pipefail
source "$(dirname "$0")/_lib.sh"
DRILL="$(resolve_drill "${1:?usage: check.sh <drill> [--label NAME]}")"
shift
python3 "$ROOT/tools/drift_check.py" "$DRILL" "$@"
