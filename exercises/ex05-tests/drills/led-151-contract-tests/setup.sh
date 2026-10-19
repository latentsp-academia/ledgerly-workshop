#!/usr/bin/env bash
# Start state for Ex 5: partial refunds (LED-101) are implemented, with no new tests yet.
set -euo pipefail
APP="${1:?usage: setup.sh <ledgerly dir>}"
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
git -C "$APP" apply "$ROOT/exercises/ex05-tests/partial-refunds.patch"
echo "  setup: partial refunds (LED-101) applied, untested"
