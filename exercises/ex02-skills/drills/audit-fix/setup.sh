#!/usr/bin/env bash
# Start state for audit-fix: LED-105 implemented the WRONG way (builds on the float legacy report,
# an ADR-0001 violation), so the audit has something to find. Records a fingerprint of src/ and
# tests/ inside .git/ (invisible to the agent) so the probe can tell whether anything was edited.
set -euo pipefail
APP="${1:?usage: setup.sh <ledgerly dir>}"
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
git -C "$APP" apply "$ROOT/exercises/ex01-claude-md/drills/led-105-revenue/reference/red.patch"
(cd "$APP" && python3 "$ROOT/exercises/ex02-skills/drills/audit-fix/fingerprint.py") > "$APP/.git/drill-audit-fix.sha"
echo "  setup: LED-105 applied with an ADR-0001 violation (uncommitted)"
