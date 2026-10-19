#!/usr/bin/env bash
# Turn the instruction-load observer on/off for ledgerly/.
#
#   tools/observe.sh on      # installs an InstructionsLoaded hook in .claude/settings.local.json
#   tools/observe.sh tail    # follow runs/loads.log while you work
#   tools/observe.sh off
#
# settings.local.json is git-ignored, so reset.sh leaves it alone.
# (Yes, this is a hook. Exercise 3 explains hooks properly; here it's just a microscope.)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/ledgerly"
SETTINGS="$APP/.claude/settings.local.json"
LOG="$ROOT/runs/loads.log"

case "${1:-}" in
  on)
    mkdir -p "$APP/.claude" "$ROOT/runs"
    if [ -f "$SETTINGS" ]; then echo "$SETTINGS already exists; not overwriting." >&2; exit 1; fi
    cat > "$SETTINGS" <<JSON
{
  "hooks": {
    "InstructionsLoaded": [
      { "hooks": [ { "type": "command", "command": "python3 \"$ROOT/tools/observer/log_loads.py\"" } ] }
    ]
  }
}
JSON
    echo "observer on -> $LOG"
    ;;
  off)
    rm -f "$SETTINGS"; echo "observer off" ;;
  tail)
    touch "$LOG"; tail -n 20 -f "$LOG" ;;
  clear)
    : > "$LOG"; echo "cleared $LOG" ;;
  *)
    echo "usage: observe.sh on|off|tail|clear" >&2; exit 1 ;;
esac
