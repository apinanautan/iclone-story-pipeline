"""Local iClone Story Pipeline MCP server.

Uses the project's existing iClone Python watcher.  All scene mutations are
queued as fixed, validated commands; no caller-provided Python is executed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(os.getenv("ICLONE_PROJECT_ROOT", Path(__file__).resolve().parent.parent)).resolve()
DATA = Path(os.getenv("ICLONE_JOB_ROOT", Path(os.environ.get("LOCALAPPDATA", str(ROOT / "_localdata"))) / "Tidmunz Studio" / "snapgen_data" / "ic8_jobs")).resolve()
RUN = DATA / "run"
RUNNER = Path(__file__).with_name("iclone_job.py")
TEXT_EXT = {".md", ".json", ".py", ".ps1", ".txt", ".log", ".yaml", ".yml"}
ALLOWED_G = Path("G:/ไดรฟ์ของฉัน").resolve()  # Only read character assets from story source


def _safe_root_file(relative_path: str) -> Path:
    if not relative_path or Path(relative_path).is_absolute() or re.search(r"(^|[/\\])\.\.([/\\]|$)", relative_path):
        raise ValueError("Use a relative path inside this project")
    resolved = (ROOT / relative_path).resolve()
    if not resolved.is_relative_to(ROOT) or any(x in {".git", "__pycache__", ".venv"} for x in resolved.relative_to(ROOT).parts):
        raise ValueError("Path outside permitted project files")
    if resolved.suffix.lower() not in TEXT_EXT:
        raise ValueError("Only project text/source files can be read")
    return resolved


def _iclone_running() -> bool:
    if os.name != "nt":
        return False
    try:
        cp = subprocess.run(["tasklist", "/FI", "IMAGENAME eq iClone.exe", "/FO", "CSV", "/NH"],
                            capture_output=True, text=True, timeout=7)
        return '"iClone.exe"' in cp.stdout
    except (OSError, subprocess.SubprocessError):
        return False


def _require_online() -> None:
    if not _iclone_running():
        raise RuntimeError("iClone.exe is not running; start iClone and load ic8_watch.py")
    if not RUN.is_dir():
        raise RuntimeError("Watcher run directory missing; load ic8_watch.py once in iClone")
    pending = sorted(p.name for p in RUN.glob("*.py"))
    if pending:
        raise RuntimeError("Existing watcher scripts pending; inspect/resolve before adding MCP jobs: " + ", ".join(pending[:5]))


def _queue(action: str, arguments: dict[str, Any]) -> dict[str, Any]:
    _require_online()
    job_id = "mcp_" + secrets.token_hex(8)
    stem = RUN / job_id
    # Stage JSON first.  The .py rename is the only enqueue action; the watcher
    # never observes a partially written Python file.
    payload = {"action": action, "args": arguments, "job_id": job_id}
    temp_json = RUN / (job_id + ".json.tmp")
    temp_py = RUN / (job_id + ".py.tmp")
    try:
        with temp_json.open("x", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        os.replace(temp_json, stem.with_suffix(".json"))
        with temp_py.open("xb") as f:
            f.write(RUNNER.read_bytes())
        os.replace(temp_py, stem.with_suffix(".py"))
    finally:
        temp_json.unlink(missing_ok=True)
        temp_py.unlink(missing_ok=True)
    return {"queued": True, "job_id": job_id, "action": action, "message": "Queued; check get_job_result for verified iClone execution"}


def _num(v: float, label: str, low: float = -1000000, high: float = 1000000) -> float:
    import math
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)) or not low <= float(v) <= high:
        raise ValueError(f"{label} must be a finite number between {low} and {high}")
    return float(v)


def _name(v: str) -> str:
    if not isinstance(v, str) or not (1 <= len(v.strip()) <= 200) or "\x00" in v:
        raise ValueError("A valid object name is required")
    return v.strip()


def get_project_status() -> dict:
    """Check the local project, iClone process, watcher marker and current job queue."""
    files = [x for x in ROOT.rglob("*") if x.is_file() and ".git" not in x.parts and "__pycache__" not in x.parts and x.suffix.lower() in TEXT_EXT]
    alive = RUN / "watcher.alive"
    return {"computer": __import__("platform").node(), "root": str(ROOT),
            "project_exists": ROOT.is_dir(), "project_text_file_count": len(files),
            "iclone_running": _iclone_running(), "watcher_marker_exists": alive.is_file(),
            "watcher_marker_is_not_heartbeat": True,
            "pending_queue_files": len(list(RUN.glob("*.py"))) if RUN.is_dir() else 0,
            "pending_queue_names": [p.name for p in list(RUN.glob("*.py"))[:5]] if RUN.is_dir() else [],
            "job_root": str(DATA), "server_version": "0.2.0",
            "next_step": "Run inspect_scene and verify its job completes to test the watcher"}


def list_project_files(folder: str = "", limit: int = 100) -> dict:
    """List source/docs under the project; excludes Git metadata and binary assets."""
    limit = int(_num(limit, "limit", 1, 300))
    target = (ROOT / folder).resolve()
    if not target.is_relative_to(ROOT) or any(part in {".git", "__pycache__", ".venv"} for part in target.relative_to(ROOT).parts):
        raise ValueError("Folder must be inside project")
    if not target.is_dir():
        raise FileNotFoundError(str(target))
    result = []
    for x in sorted(target.rglob("*")):
        if x.is_file() and x.suffix.lower() in TEXT_EXT and not set(x.parts).intersection({".git", "__pycache__", ".venv"}):
            result.append({"path": x.relative_to(ROOT).as_posix(), "bytes": x.stat().st_size})
            if len(result) >= limit:
                break
    return {"files": result, "limit": limit}


def read_project_file(path: str, max_chars: int = 16000) -> dict:
    """Read a permitted source/configuration file relative to project root."""
    max_chars = int(_num(max_chars, "max_chars", 1, 50000))
    fp = _safe_root_file(path)
    if fp.stat().st_size > 500000:
        raise ValueError("File exceeds 500KB; narrow the requested source")
    text = fp.read_text(encoding="utf-8-sig", errors="replace")
    return {"path": fp.relative_to(ROOT).as_posix(), "text": text[:max_chars], "truncated": len(text) > max_chars, "length": len(text)}


def get_rules() -> dict:
    """Read current project instructions, rules and scene anchors (live files)."""
    return {p: read_project_file(p, 30000)["text"] for p in ["AGENTS.md", "docs/rules.md", "docs/scene_anchors.md"]}


def list_jobs(limit: int = 15) -> dict:
    """List recent MCP-managed jobs without reading unrelated watcher jobs."""
    limit = int(_num(limit, "limit", 1, 50))
    if not RUN.is_dir():
        return {"jobs": []}
    js = sorted((p for p in RUN.glob("mcp_*.json") if re.fullmatch(r"mcp_[0-9a-f]{16}\.json", p.name)), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    return {"jobs": [get_job_result(p.stem, include_log=False) for p in js]}


def get_job_result(job_id: str, include_log: bool = True) -> dict:
    """Get a queued job state and its inner result JSON; `.done` alone is not proof of success."""
    if not re.fullmatch(r"mcp_[0-9a-f]{16}", job_id):
        raise ValueError("Invalid job ID")
    stem = RUN / job_id
    if not stem.with_suffix(".json").is_file():
        raise FileNotFoundError("Unknown MCP job")
    status = "queued" if stem.with_suffix(".py").exists() else (
        "watcher_error" if stem.with_suffix(".err").exists() else (
        "watcher_done" if stem.with_suffix(".done").exists() else "unknown"))
    result: dict[str, Any] = {"job_id": job_id, "watcher_state": status}
    result_file = RUN / (job_id + ".result.json")
    if result_file.exists():
        try:
            inner = json.loads(result_file.read_text(encoding="utf-8"))
            result["result"] = inner
            result["complete"] = status in {"watcher_done", "watcher_error"}
            result["success"] = bool(inner.get("ok")) and status == "watcher_done"
        except (json.JSONDecodeError, UnicodeError):
            result["result_error"] = "Malformed inner result"
    if include_log and stem.with_suffix(".log").exists():
        result["watcher_log_tail"] = stem.with_suffix(".log").read_text(encoding="utf-8", errors="replace")[-3500:]
    return result


def inspect_scene() -> dict:
    """Queue a READ-ONLY inventory of avatars, props, cameras and lights in the open iClone scene."""
    return _queue("inspect_scene", {})


def inspect_timeline() -> dict:
    """Queue a READ-ONLY timeline report: fps, duration, avatar animation clips."""
    return _queue("inspect_timeline", {})


def place_existing_avatar(name: str, x: float, y: float, z: float, yaw: float, confirm_change: bool = False) -> dict:
    """Position an already-loaded avatar at frame zero, with explicit permission to change the scene."""
    if not confirm_change:
        raise ValueError("Scene change requires confirm_change=true after user's instruction")
    return _queue("place_existing_avatar", {"name": _name(name), "x": _num(x, "x"), "y": _num(y, "y"),
                                             "z": _num(z, "z"), "yaw": _num(yaw, "yaw", -360, 360)})


def set_project_duration(seconds: float, confirm_change: bool = False) -> dict:
    """Set both project length and timeline end time (seconds including +5s tail)."""
    if not confirm_change:
        raise ValueError("Scene change requires confirm_change=true")
    return _queue("set_project_duration", {"seconds": _num(seconds, "seconds", 0.1, 7200)})


def set_auto_blink(name: str, confirm_change: bool = False) -> dict:
    """Enable Normal auto-blink for one already loaded avatar."""
    if not confirm_change:
        raise ValueError("Scene change requires confirm_change=true")
    return _queue("set_auto_blink", {"name": _name(name)})


def apply_part2_face_lips(name: str, confirm_change: bool = False) -> dict:
    """DEPRECATED: Old WAV-based workflow is prohibited by the user's full-MP3/iClone-trim rule."""
    raise RuntimeError(
        "Deprecated lip-sync method: do NOT import externally cut WAV files. "
        "In iClone, select the speaker, import full N.mp3 via Create Script > "
        "AccuLips/Voice, then split/trim the unused portions inside the "
        "Viseme/Voice timeline and verify mouth movements. See docs/rules.md."
    )


def set_existing_camera(name: str, x: float, y: float, z: float,
                        target_x: float, target_y: float, target_z: float,
                        focal_mm: int = 100, dof: bool = True, confirm_change: bool = False) -> dict:
    """Aim an existing camera using a 80/100mm lens, with optional subject DOF."""
    if not confirm_change:
        raise ValueError("Scene change requires confirm_change=true")
    if focal_mm not in (80, 100):
        raise ValueError("User rule: lens must be 80 or 100 mm")
    pos = [_num(v, f"camera_{i}") for i, v in enumerate((x, y, z))]
    target = [_num(v, f"target_{i}") for i, v in enumerate((target_x, target_y, target_z))]
    if sum((a-b)**2 for a,b in zip(pos,target)) < 100:
        raise ValueError("Camera must be at least 10 scene units from target")
    return _queue("set_existing_camera", {"name": _name(name), "pos": pos, "target": target, "focal": focal_mm, "dof": bool(dof)})


def build_part2_camera_sequence(confirm_change: bool = False) -> dict:
    """Create fixed 9-shot Part 2 camera/switcher keys, verify poses and make nine still previews."""
    if not confirm_change:
        raise ValueError("Editing Part 2 cameras requires user's instruction and confirm_change=true")
    return _queue("build_part2_camera_sequence", {})


def retune_part2_group_shot(shot_index: int, pos_x: float, pos_y: float, pos_z: float,
                            target_x: float, target_y: float, target_z: float,
                            confirm_change: bool = False) -> dict:
    """Reframe existing switcher shot 7 or 9; preview without touching actors."""
    if not confirm_change:
        raise ValueError("Explicit scene change authorization is required")
    if shot_index not in (7, 9):
        raise ValueError("Only group shots 7 and 9 may be adjusted here")
    xyz = [_num(pos_x, "x", -450, 450), _num(pos_y,"y",-50,1250),
           _num(pos_z,"z",25760,26300)]
    target = [_num(target_x,"tx",-150,200),_num(target_y,"ty",350,970),
              _num(target_z,"tz",25760,26300)]
    if sum((x-t)**2 for x,t in zip(xyz,target)) < 300**2:
        raise ValueError("Group camera must be at least 300 scene units from focus")
    return _queue("retune_part2_group_shot", {"shot_index": shot_index,
                                            "pos": xyz,"target": target})


def inspect_part2_lip_sync() -> dict:
    """Read-only introspection of available voice/viseme/audio APIs for Part 2 avatars."""
    return _queue("inspect_part2_lip_sync", {})


def preview_part2_switcher() -> dict:
    """Read-only six-frame preview of the selected Switch camera at cut-separated times."""
    return _queue("preview_part2_switcher", {})


def retune_part2_shot(shot_index: int, pos_x: float, pos_y: float, pos_z: float,
                      target_x: float, target_y: float, target_z: float,
                      focal_mm: int = 100, confirm_change: bool = False) -> dict:
    """Reframe one of the nine existing Part 2 shots with 80/100mm lens and a fresh still."""
    if not confirm_change:
        raise ValueError("Explicit scene change authorization required")
    if isinstance(shot_index, bool) or shot_index not in range(1,10):
        raise ValueError("Shot index 1..9")
    if focal_mm not in (80,100):
        raise ValueError("Only 80 or 100mm lenses")
    xyz = [_num(pos_x,"x",-650,650), _num(pos_y,"y",-300,1500),
           _num(pos_z,"z",25770,26300)]
    target = [_num(target_x,"tx",-400,400), _num(target_y,"ty",300,1200),
              _num(target_z,"tz",25770,26200)]
    if sum((x-t)**2 for x,t in zip(xyz,target)) < 120**2:
        raise ValueError("Camera must be at least 120 scene units from target")
    return _queue("retune_part2_shot",{"shot_index":shot_index,"pos":xyz,
            "target":target,"focal":focal_mm})


def preview_camera_still(name: str, seconds: float = 2.0) -> dict:
    """Render a single temporary preview PNG for an existing camera (never render an MP4)."""
    if name not in {"Camera", "Camera_0"}:
        raise ValueError("Only existing Part 2 scene cameras are allowed")
    return _queue("preview_camera_still", {"name": name,
                                              "seconds": _num(seconds, "seconds", 0.0, 86.5)})


def render_part(part_number: int, end_seconds: float, confirm_render: bool = False) -> dict:
    """Render an explicitly authorized part to E:/Video/N.mp4 at 1920x1080 60fps. Never overwrites."""
    if not confirm_render:
        raise ValueError("Explicit render instruction and confirm_render=true required")
    if isinstance(part_number, bool) or not isinstance(part_number, int) or not 1 <= part_number <= 9999:
        raise ValueError("part_number must be an integer 1-9999")
    duration = _num(end_seconds, "end_seconds", 0.2, 7200)
    path = Path(f"E:/Video/{part_number}.mp4")
    if path.exists():
        raise FileExistsError(f"Output exists; refusing to overwrite: {path}")
    return _queue("render_part", {"part_number": part_number, "end_seconds": duration, "out": str(path)})


def verify_part_output(part_number: int) -> dict:
    """Check whether the expected iProject and MP4 exist; optionally probe video with ffprobe."""
    if isinstance(part_number, bool) or not isinstance(part_number, int) or not 1 <= part_number <= 9999:
        raise ValueError("part_number must be an integer 1-9999")
    out: dict[str, Any] = {"part": part_number}
    for label, path in [("project", Path(f"E:/FileSave/{part_number}.iProject")),
                        ("video", Path(f"E:/Video/{part_number}.mp4"))]:
        out[label] = {"path": str(path), "exists": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0}
    # Optional: only if ffprobe is installed at known ffmpeg tools path.
    probe = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes" / "tools" / "ffmpeg-9.0.1-win32-x64" / "bin" / "ffprobe.exe"
    if out["video"]["exists"] and probe.is_file():
        try:
            p = subprocess.run([str(probe), "-v", "error", "-show_entries", "format=duration", "-show_entries", "stream=width,height,r_frame_rate", "-of", "json", str(out["video"]["path"])], capture_output=True, text=True, timeout=15)
            if p.returncode == 0:
                out["video"]["probe"] = json.loads(p.stdout)
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
            pass
    return out


TOOLS = [get_project_status, list_project_files, read_project_file, get_rules, list_jobs,
         get_job_result, inspect_scene, inspect_timeline, place_existing_avatar,
         set_project_duration, set_auto_blink, apply_part2_face_lips, set_existing_camera, preview_camera_still, build_part2_camera_sequence, retune_part2_group_shot, retune_part2_shot, preview_part2_switcher, inspect_part2_lip_sync, render_part, verify_part_output]


def main() -> None:
    parser = argparse.ArgumentParser(description="iClone Story Pipeline MCP server")
    parser.add_argument("--cli", action="store_true", help="Use one tool through Dino Tunnel/shell (no MCP client needed)")
    parser.add_argument("--http", action="store_true", help="Loopback HTTP MCP server (localhost only, no public access)")
    parser.add_argument("name", nargs="?", help="Tool name for --cli")
    parser.add_argument("args", nargs="?", default="{}", help="JSON object arguments for --cli")
    parsed = parser.parse_args()
    if parsed.cli:
        raw = parsed.args
        if parsed.name == "get_job_result" and re.fullmatch(r"mcp_[0-9a-f]{16}", raw):
            options = {"job_id": raw}
        elif raw.startswith("@"):
            options = json.loads(Path(raw[1:]).read_text(encoding="utf-8"))
        else:
            options = json.loads(raw)
        if not isinstance(options, dict):
            raise ValueError("Arguments must be a JSON object")
        f = {x.__name__: x for x in TOOLS}.get(parsed.name)
        if f is None:
            raise ValueError("Unknown tool: " + str(parsed.name))
        try:
            result = {"ok": True, "data": f(**options)}
        except Exception as ex:
            result = {"ok": False, "error": type(ex).__name__ + ": " + str(ex)}
        print(json.dumps(result, ensure_ascii=False, default=str))
        return
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("iClone Story Pipeline", instructions="Use for authorized local iClone 8 inspection, staging and rendering. Read project rules first. Never render without user request.", host="127.0.0.1", port=8766)
    for tool in TOOLS:
        mcp.add_tool(tool)
    mcp.run(transport="streamable-http" if parsed.http else "stdio")


if __name__ == "__main__":
    main()
