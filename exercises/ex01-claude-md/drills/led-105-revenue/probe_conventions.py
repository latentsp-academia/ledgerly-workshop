"""Hidden convention test for Ledgerly value objects. Run from ledgerly/ (the checker does this).

The agent never sees this file: it lives in the drill folder, outside the repo. So the only way
the agent can know the convention is from a memory file (.claude/rules/value-objects.md).

Convention (Ledgerly house style):
  1. Business logic for a ticket lands in services/: at least one new public function there.
  2. New classes under services/ and payments/ are value objects:
       @dataclass(frozen=True, slots=True, kw_only=True)
     Exceptions, enums and protocols are exempt.
  3. Service functions never return dicts (dict / Dict / Mapping / TypedDict). They return
     value objects; the API maps them to pydantic response models.

Only code added since the `baseline` tag is graded. Legacy code (services/reports.py) is not.
"""

from __future__ import annotations

import ast
import subprocess
import sys

PATHS = ("src/ledgerly/services", "src/ledgerly/payments")
REQUIRED = ("frozen", "slots", "kw_only")
EXEMPT_BASES = {"Exception", "BaseModel", "Enum", "IntEnum", "StrEnum", "Protocol"}
DICTISH = ("dict", "Dict", "Mapping", "MutableMapping", "TypedDict")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout


def changed_py_files() -> list[str]:
    tracked = git("diff", "baseline", "--name-only", "--", *PATHS).split()
    untracked = git("ls-files", "--others", "--exclude-standard", "--", *PATHS).split()
    return sorted(f for f in set(tracked) | set(untracked) if f.endswith(".py"))


def parse(src: str) -> ast.Module:
    try:
        return ast.parse(src)
    except SyntaxError:
        return ast.parse("")


def top_level(tree: ast.Module) -> tuple[dict[str, ast.ClassDef], dict[str, ast.FunctionDef]]:
    classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    return classes, funcs


def base_names(cls: ast.ClassDef) -> list[str]:
    out = []
    for b in cls.bases:
        if isinstance(b, ast.Name):
            out.append(b.id)
        elif isinstance(b, ast.Attribute):
            out.append(b.attr)
    return out


def is_exempt(cls: ast.ClassDef) -> bool:
    for b in base_names(cls):
        if b in EXEMPT_BASES or b.endswith(("Error", "Exception")):
            return True
    return False


def dataclass_flags(cls: ast.ClassDef) -> set[str] | None:
    """Keyword flags set to True on @dataclass(...); None if not a dataclass at all."""
    for d in cls.decorator_list:
        target = d.func if isinstance(d, ast.Call) else d
        name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", "")
        if name != "dataclass":
            continue
        if not isinstance(d, ast.Call):
            return set()
        return {
            k.arg
            for k in d.keywords
            if k.arg and isinstance(k.value, ast.Constant) and k.value.value is True
        }
    return None


def main() -> int:
    problems: list[str] = []
    new_service_funcs: list[str] = []

    for path in changed_py_files():
        now = parse(open(path).read())
        before = parse(git("show", f"baseline:{path}"))
        classes, funcs = top_level(now)
        old_classes, old_funcs = top_level(before)

        for name, cls in classes.items():
            if name in old_classes or is_exempt(cls):
                continue
            flags = dataclass_flags(cls)
            if flags is None:
                problems.append(f"{name} is not a dataclass (house style: frozen+slots+kw_only) in {path}")
                continue
            missing = [f for f in REQUIRED if f not in flags]
            if missing:
                problems.append(
                    f"{name} missing {', '.join(m + '=True' for m in missing)} "
                    f"(house style: frozen+slots+kw_only) in {path}"
                )
            if any(b in ("TypedDict", "NamedTuple") for b in base_names(cls)):
                problems.append(f"{name} subclasses {', '.join(base_names(cls))}; use a dataclass ({path})")

        if path.startswith("src/ledgerly/services/"):
            for name, fn in funcs.items():
                if name.startswith("_") or name in old_funcs:
                    continue
                new_service_funcs.append(f"{path}:{name}")
                ret = ast.unparse(fn.returns) if fn.returns is not None else ""
                if any(word in ret for word in DICTISH):
                    problems.append(f"{name}() returns {ret}; services return value objects, not dicts ({path})")

    if not new_service_funcs:
        problems.insert(0, "no new public function in services/: the logic was written outside the service layer")

    if problems:
        print(problems[0] + (f"  (+{len(problems) - 1} more)" if len(problems) > 1 else ""))
        for p in problems[1:]:
            print("   " + p, file=sys.stderr)
        return 1
    print(f"value objects OK ({len(new_service_funcs)} new service function(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
