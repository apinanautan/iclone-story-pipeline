"""iClone 8 OpenPlugin auto-loader for the existing project watcher.

On every iClone start, load the watcher ONLY if the run queue is empty.
Reallusion calls initialize_plugin() from OpenPlugin/<name>/main.py.
"""
import glob
import os
import runpy
import traceback


def initialize_plugin():
    local = os.environ.get("LOCALAPPDATA", "")
    jobs = os.path.join(local, "Tidmunz Studio", "snapgen_data", "ic8_jobs")
    run = os.path.join(jobs, "run")
    watcher = r"C:\Users\Apinan\Documents\iClone Story Pipeline\scripts\ic8_watch.py"
    status = ""
    try:
        pending = glob.glob(os.path.join(run, "*.py"))
        if pending:
            status = "BLOCKED: existing pending .py jobs: " + ", ".join(os.path.basename(p) for p in pending[:10])
        elif not os.path.isfile(watcher):
            status = "BLOCKED: watcher source not found"
        else:
            runpy.run_path(watcher, run_name="__main__")
            status = "STARTED: ic8_watch.py loaded by OpenPlugin"
    except Exception:
        status = "ERROR: " + traceback.format_exc()
    try:
        os.makedirs(jobs, exist_ok=True)
        with open(os.path.join(jobs, "mcp_autostart_status.txt"), "w", encoding="utf-8") as f:
            f.write(status + "\n")
    except Exception:
        pass
    print("iCloneStoryBridge: " + status[:1000])
