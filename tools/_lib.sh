# Shared helpers, sourced by the other scripts. Bash 3.2 compatible (macOS default).

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/ledgerly"

# resolve_drill led-105  ->  /…/exercises/ex01-claude-md/drills/led-105-revenue
resolve_drill() {
  local arg="$1"
  if [ -d "$arg" ] && [ -f "$arg/checks.json" ]; then (cd "$arg" && pwd); return 0; fi
  local hits n
  hits="$(find "$ROOT/exercises" -type f -path "*/drills/$arg*/checks.json" 2>/dev/null | sort)"
  n="$(printf '%s' "$hits" | grep -c . || true)"
  if [ "$n" = "1" ]; then dirname "$hits"; return 0; fi
  if [ "$n" -gt 1 ]; then
    echo "'$arg' matches several drills, be more specific:" >&2
    printf '%s\n' "$hits" | sed "s|$ROOT/||; s|/checks.json||; s|^|  |" >&2
    return 1
  fi
  echo "no drill matching '$arg' (try: led-100, led-105, led-112, led-103, led-120, trigger-implicit, trigger-quiet, led-132, led-141, led-150, led-151, led-118)" >&2
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
