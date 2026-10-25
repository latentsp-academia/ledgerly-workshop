"""Release gate: the version only changes in a turn where a human typed /release.

UserPromptSubmit: remember (per session) whether this prompt starts with /release.
PreToolUse: block running bump.py, or editing pyproject.toml, unless that turn was armed.
disable-model-invocation stops Claude from *calling* the skill; this stops it from doing the
release by hand from the files on disk.
"""

import json
import sys
import tempfile
from pathlib import Path

event = json.load(sys.stdin)
flag = Path(tempfile.gettempdir()) / f"ledgerly-release-{event.get('session_id', 'x')}"

if event.get("hook_event_name") == "UserPromptSubmit":
    if event.get("prompt", "").lstrip().startswith("/release"):
        flag.touch()
    else:
        flag.unlink(missing_ok=True)
    sys.exit(0)

tool, args = event.get("tool_name", ""), event.get("tool_input", {})
releasing = (tool == "Bash" and "bump.py" in args.get("command", "")) or (
    tool in ("Edit", "Write", "MultiEdit") and str(args.get("file_path", "")).endswith("pyproject.toml")
)
if releasing and not flag.exists():
    print(
        "Blocked by the release gate: versions change only when a human types /release. "
        "Write the notes as text instead, and tell the user to run /release.",
        file=sys.stderr,
    )
    sys.exit(2)
