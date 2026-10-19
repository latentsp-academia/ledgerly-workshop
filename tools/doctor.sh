#!/usr/bin/env bash
# Ex 0 · Is this machine ready for the workshop? Read-only: changes nothing except `uv sync`.
#
#   tools/doctor.sh            # every check, then a summary
#   tools/doctor.sh --quick    # skip the test/lint gates (tools only)
#
# Bash 3.2 compatible (macOS default).
set -uo pipefail
source "$(dirname "$0")/_lib.sh"
QUICK="${1:-}"
FAILS=0
WARNS=0

ok()   { printf '   \033[32mPASS\033[0m  %-26s %s\n' "$1" "${2:-}"; }
bad()  { printf '   \033[31mFAIL\033[0m  %-26s %s\n' "$1" "$2"; FAILS=$((FAILS + 1)); }
warn() { printf '   \033[33mWARN\033[0m  %-26s %s\n' "$1" "$2"; WARNS=$((WARNS + 1)); }

need() {  # need <id> <command> <how to install>
  if command -v "$2" >/dev/null 2>&1; then
    ok "$1" "$("$2" --version 2>/dev/null | head -1)"
  else
    bad "$1" "not found. $3"
  fi
}

echo "Tools"
need claude claude "Install Claude Code: https://code.claude.com"
need uv uv "Install uv: https://docs.astral.sh/uv/getting-started/installation/"
need git git "Install git (macOS: xcode-select --install)"
if command -v python3 >/dev/null 2>&1 &&
   python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'; then
  ok python3 "$(python3 --version 2>&1) (runs the checker and the hooks)"
else
  bad python3 "python3 3.9+ needed for tools/ and the Ex 3 hooks"
fi
if command -v cursor >/dev/null 2>&1; then ok cursor "optional, for the Cursor sidebars"
else warn cursor "optional. Only needed for the Cursor sidebars"; fi

echo "Sample app"
if [ -e "$APP/.git" ] && git -C "$APP" rev-parse --git-dir >/dev/null 2>&1; then
  ok ledgerly-repo "ledgerly/ is a local repo (made by tools/setup.sh)"
  if git -C "$APP" rev-parse -q --verify refs/tags/baseline >/dev/null; then
    ok baseline-tag "tools/reset.sh returns here"
  else
    bad baseline-tag "tag 'baseline' missing in ledgerly/. Remove ledgerly/.git, then run tools/setup.sh"
  fi
  CHANGED="$(git -C "$APP" status --porcelain | grep -c . || true)"
  if [ "$CHANGED" = "0" ]; then ok clean-start "ledgerly/ matches baseline"
  else warn clean-start "$CHANGED changed/untracked file(s) in ledgerly/. Fine mid-workshop; tools/reset.sh before Ex 1"; fi
else
  bad ledgerly-repo "ledgerly/ isn't a git repo. Run tools/setup.sh"
fi
if [ -f "$HOME/.claude/CLAUDE.md" ]; then
  warn user-claude-md "~/.claude/CLAUDE.md exists and loads into every session. Drill results may differ from the room's"
fi

if [ "$QUICK" != "--quick" ] && command -v uv >/dev/null 2>&1; then
  echo "Gates (the same ones the agent must pass)"
  if uv --directory "$APP" sync -q >/dev/null 2>&1; then ok uv-sync "ledgerly/.venv ready"
  else bad uv-sync "uv --directory ledgerly sync failed. Run it to see why (network? proxy?)"; fi
  OUT="$(uv --directory "$APP" run pytest -q 2>&1 | tail -1)"
  case "$OUT" in *passed*) case "$OUT" in *failed*|*error*) bad pytest "$OUT";; *) ok pytest "$OUT";; esac;;
                 *) bad pytest "${OUT:-no output}";; esac
  if uv --directory "$APP" run ruff check -q . >/dev/null 2>&1; then ok ruff "lint clean"
  else bad ruff "ruff reports issues in ledgerly/ (an earlier exercise left changes? tools/reset.sh)"; fi
  if (cd "$APP" && uv run lint-imports >/dev/null 2>&1); then ok import-linter "2 contracts kept (layers, no legacy FX)"
  else bad import-linter "a layer contract is broken (tools/reset.sh?)"; fi
fi

echo
if [ "$FAILS" -gt 0 ]; then
  printf '   => \033[31mNOT READY\033[0m (%s failing, %s warnings)\n' "$FAILS" "$WARNS"; exit 1
fi
printf '   => \033[32mREADY\033[0m (%s warnings)\n' "$WARNS"
