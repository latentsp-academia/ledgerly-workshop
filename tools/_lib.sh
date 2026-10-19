# Shared helpers, sourced by the other scripts. Bash 3.2 compatible (macOS default).

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/ledgerly"

# resolve_drill led-105  ->  /…/exercises/ex01-claude-md/drills/led-105-revenue
resolve_drill() {
  local arg="$1" hit
  if [ -d "$arg" ] && [ -f "$arg/checks.json" ]; then (cd "$arg" && pwd); return 0; fi
  hit="$(find "$ROOT/exercises" -type d -path "*/drills/$arg*" 2>/dev/null | head -1)"
  if [ -n "$hit" ] && [ -f "$hit/checks.json" ]; then echo "$hit"; return 0; fi
  echo "no drill matching '$arg' (try: led-105, led-112, led-103)" >&2
  return 1
}

# resolve_variant <drill-dir> <name-or-path>  ->  directory to copy into ledgerly/
resolve_variant() {
  local drill="$1" v="$2"
  if [ -d "$v" ]; then (cd "$v" && pwd); return 0; fi
  if [ -d "$drill/variants/$v" ]; then echo "$drill/variants/$v"; return 0; fi
  if [ -d "$ROOT/my-variants/$v" ]; then echo "$ROOT/my-variants/$v"; return 0; fi
  echo "no variant '$v' (a folder path, $drill/variants/$v, or my-variants/$v)" >&2
  return 1
}
