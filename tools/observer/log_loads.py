#!/usr/bin/env python3
"""InstructionsLoaded hook: append one line per instruction file Claude loads.

This is a microscope, not a gate: it can't block anything. It answers the "load check"
question deterministically: which CLAUDE.md / rules file entered the context, when, and why.
Installed by tools/observe.sh on. Log: runs/loads.log
"""

import json
import sys
import time
from pathlib import Path

LOG = Path(__file__).resolve().parents[2] / "runs" / "loads.log"

try:
    event = json.load(sys.stdin)
except Exception:
    sys.exit(0)

cwd = event.get("cwd", "")


def short(p: str) -> str:
    if not p:
        return "-"
    return p.replace(str(Path.home()), "~").replace(cwd + "/", "")


LOG.parent.mkdir(parents=True, exist_ok=True)
with LOG.open("a") as fh:
    fh.write(
        "{ts}  {reason:<17} {scope:<8} {file:<45} {trigger}\n".format(
            ts=time.strftime("%H:%M:%S"),
            reason=event.get("load_reason", "?"),
            scope=event.get("memory_type", "?"),
            file=short(event.get("file_path", "")),
            trigger=("<- " + short(event["trigger_file_path"]))
            if event.get("trigger_file_path")
            else "",
        )
    )
sys.exit(0)
