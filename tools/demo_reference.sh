#!/usr/bin/env bash
# Facilitator fallback: show a drill's red or green without a live agent run.
# Applies the drill's hand-written reference patch (+ synthetic transcript) and checks it.
#
#   tools/demo_reference.sh led-105 red
#   tools/demo_reference.sh led-103 green
#
# The patches reproduce what agents typically do. They are NOT recordings. Say so in the room,
# and record your own runs with run_drill.sh before class.
set -euo pipefail
source "$(dirname "$0")/_lib.sh"
DRILL="$(resolve_drill "${1:?usage: demo_reference.sh <drill> red|green}")"
WHICH="${2:?red|green}"
"$ROOT/tools/reset.sh" >/dev/null
if [ -s "$DRILL/reference/$WHICH.patch" ]; then
  git -C "$APP" apply "$DRILL/reference/$WHICH.patch"
  echo "applied reference/$WHICH.patch — inspect with: git -C ledgerly diff baseline"
else
  echo "reference/$WHICH.patch is empty: the right outcome here is to change nothing."
fi
T="$DRILL/reference/$WHICH.synthetic.jsonl"
[ -f "$T" ] || T=none
python3 "$ROOT/tools/drift_check.py" "$DRILL" --transcript "$T" --label "reference-$WHICH" \
  --out "$ROOT/runs/reference" || true
