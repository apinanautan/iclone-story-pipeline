"""Ai-iclone MCP server: lets ChatGPT (via Dino Tunnel) or any MCP client run the same step 1..N flow as every AI.

Each tool runs one Ai-iclone command (scripts/ai_iclone.py) and returns its text. There are no part-specific
tools and no free Python: Ai-iclone decides the next step, stops at user steps, and needs the user's own words
to approve. Rebuilt 2026-11-22 (the old version had ~20 fixed tools, many only for part 2).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.getenv("ICLONE_PROJECT_ROOT", Path(__file__).resolve().parent.parent)).resolve()
APP = ROOT / "scripts" / "ai_iclone.py"
TIMEOUT = 3600  # one step (render is the longest); Ai-iclone's own steps have their own hard timeouts
EXIT = {0: "OK", 1: "FAIL", 2: "STOP: tell the user and wait", 3: "AI WORK: do what the card says, then call do_next_step"}

GUIDE = """Ai-iclone makes a 3D story video in iClone 8, one part at a time, in fixed steps 1..N.
Loop: status -> do_next_step -> read the reply -> repeat.
 - reply ends 'OK'        : call do_next_step again.
 - 'AI WORK'              : follow the rules card in the reply (fill the named file), then do_next_step.
 - 'STOP'                 : tell the user in Thai what is needed and WAIT. Never approve for the user.
 - 'FAIL'                 : one retry at most; a 2nd FAIL stops by itself.
Approve only with the user's exact words: approve(user_said=...). Answer the user in Thai."""


def _run(*args: str) -> str:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        cp = subprocess.run([sys.executable, str(APP), *args], cwd=ROOT, env=env, capture_output=True, stdin=subprocess.DEVNULL,  # never share the MCP stdio pipe
                            text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return "FAIL: Ai-iclone %s took over %d s (stopped). Tell the user." % (" ".join(args), TIMEOUT)
    text = (cp.stdout + ("\n" + cp.stderr if cp.stderr.strip() else "")).strip()
    return text + "\n\n[Ai-iclone exit %d = %s]" % (cp.returncode, EXIT.get(cp.returncode, "FAIL"))


def _need(value: str, what: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ValueError(what + " is required")
    return value.strip()


def status() -> str:
    """Where the work is now (story, part, step) and the next command. Call this first."""
    return _run("status")


def steps() -> str:
    """All steps 1..N of the current story and part, with done / todo."""
    return _run("steps")


def rules(step: str) -> str:
    """The rules card for one step (what to do and what not to do)."""
    return _run("rules", _need(step, "step"))


def do_next_step(dry: bool = False, retry: bool = False) -> str:
    """Do the NEXT step only (one per call). dry=True shows what would run. retry=True only after the user said to try again."""
    return _run("do", *(["--dry"] if dry else []), *(["--force"] if retry else []))


def use_part(story: str, part: str = "") -> str:
    """Switch to a story (and part number) the user named."""
    return _run("use", _need(story, "story"), *([str(part).strip()] if str(part).strip() else []))


def new_story(story: str) -> str:
    """Start a new story the user asked for."""
    return _run("new-story", _need(story, "story"))


def set_range(time_range: str) -> str:
    """The time range of this part that the user typed, e.g. '1:05-2:10'."""
    return _run("range", _need(time_range, "time_range"))


def approve(user_said: str) -> str:
    """Record the user's approval. user_said = the user's own words, copied exactly. Never invent it."""
    return _run("approve", "--said", _need(user_said, "user_said"))


def clean_temp_files() -> str:
    """Delete old iClone temp files (older than 2 days) and backups. Only when the user asks or status warns."""
    return _run("clean")


def version() -> str:
    """Ai-iclone version."""
    return _run("version")


TOOLS = [status, steps, rules, do_next_step, use_part, new_story, set_range, approve, clean_temp_files, version]


def main() -> None:
    p = argparse.ArgumentParser(description="Ai-iclone MCP server (stdio). --cli runs one tool from a shell / Dino Tunnel.")
    p.add_argument("--cli", action="store_true", help='one tool, e.g. --cli status  or  --cli do_next_step "{\\"dry\\": true}"')
    p.add_argument("--http", action="store_true", help="loopback HTTP 127.0.0.1:8766 (no auth: never expose)")
    p.add_argument("name", nargs="?")
    p.add_argument("args", nargs="?", default="{}")
    a = p.parse_args()
    if a.cli:
        f = {t.__name__: t for t in TOOLS}.get(a.name)
        if f is None:
            print("tools: " + ", ".join(t.__name__ for t in TOOLS)); sys.exit(1)
        opts = json.loads(Path(a.args[1:]).read_text(encoding="utf-8") if a.args.startswith("@") else a.args)
        sys.stdout.reconfigure(encoding="utf-8")
        print(f(**opts))
        return
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("Ai-iclone", instructions=GUIDE, host="127.0.0.1", port=8766)
    for t in TOOLS:
        mcp.add_tool(t)
    mcp.run(transport="streamable-http" if a.http else "stdio")


if __name__ == "__main__":
    main()
