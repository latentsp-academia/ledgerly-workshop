#!/usr/bin/env bash
# Start state for LED-120: LED-105 (revenue endpoint) is already implemented on this branch,
# uncommitted, exactly as Exercise 1's reference solution wrote it. The task is to review-ready it.
set -euo pipefail
APP="${1:?usage: setup.sh <ledgerly dir>}"
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
git -C "$APP" apply "$ROOT/exercises/ex01-claude-md/drills/led-105-revenue/reference/green.patch"
echo "  setup: LED-105 implementation applied (uncommitted)"
