"""Pure workflow invalidation rules; no GUI or project side effects."""
def invalidated_steps(step, order):
    after = order[order.index(step) + 1:] if step in order and not step.endswith("check") else []
    if step == "sound":
        # Replacing audio needs fresh lip sync and delivery validation, not pose.
        after = [k for k in after if k in ("lip","face_check","editorial_review","switch","ready","render","video_check","final_review")]
    if step == "lip":
        after = [k for k in after if k in ("face_check","editorial_review","switch","ready","render","video_check","final_review")]
    if step == "render":
        after = ["video_check","final_review"]
    if step == "video_check": after=["final_review"]
    if step in ("cam_check","motion_check","light_check","face_check"):
        # A read-only recheck does not change existing geometry, motion, lights or cameras.
        after=[k for k in order[order.index(step)+1:] if k in ("editorial_review","switch","ready","render","video_check","final_review")]
    if step == "motion_plan":
        after = order[order.index("pose"):]
    if step in ("cast", "pose", "motion_plan"):
        # Same loaded project: keep the existing Project Sound.
        after = [k for k in after if k != "sound"]
    return [step] + after


def sound_source(wav):
    """Receipt for the exact source successfully imported by the native sound step."""
    import os
    p = os.path.normcase(os.path.abspath(wav))
    st = os.stat(p)
    return {"path": p, "size": st.st_size, "mtime_ns": st.st_mtime_ns}


def source_changed(receipt, wav):
    """Legacy completion markers remain valid until explicit repair or a new project."""
    if not receipt:
        return False
    try:
        return receipt != sound_source(wav)
    except OSError:
        return True


def expected_live_title(project, title):
    import os
    return bool(title and title.rstrip(" *") == "iClone 8 - " + os.path.basename(project))


def menu_save_verified(project, proof, title):
    """Observe a nonempty newer file and clean live title; not an integrity test."""
    import os
    if not expected_live_title(project,title) or title.rstrip().endswith("*"):return False
    try:
        st=os.stat(project)
        return st.st_size>0 and st.st_mtime_ns>int(proof["baseline_mtime_ns"])
    except (OSError,ValueError,TypeError,KeyError):return False


def unsaved_live_part(root):
    from pathlib import Path
    from cinematic_qa import read
    for p in (Path(root)/"progress").glob("*.json"):
        d=read(p)
        if isinstance(d,dict) and d.get("ready_menu_save",{}).get("live_render_pending_save"):
            return p.stem
    return None


def selected_target(root, story=None):
    from pathlib import Path
    import json
    p=Path(root)/"progress"
    def load(name):
        try:return json.loads((p/name).read_text(encoding="utf-8-sig"))
        except (OSError,ValueError):return {}
    session=load("sleep_session.json")
    sel=session if session.get("enabled") else load("ai_iclone.json")
    if sel.get("story") and sel.get("part") is not None and (story is None or story==sel["story"]):
        return {"story":sel["story"],"part":str(sel["part"])}
    return {}


def active_context(root):
    from pathlib import Path
    import json
    from preview_gate import reconcile_orphaned_run
    now=reconcile_orphaned_run(root)
    target=selected_target(root)
    if target and (now.get("story"),str(now.get("part")))!=(target["story"],target["part"]):
        return dict(target,step=None,state="selected")
    return now

def live_snapshot():
    """Read the native window and process identity, never infer it from progress files."""
    import subprocess, json
    cmd = "[Console]::OutputEncoding=[Text.Encoding]::UTF8;$p=@(Get-Process iClone -EA 0 | Where-Object MainWindowHandle -ne 0);if($p.Count -eq 1){@{title=$p[0].MainWindowTitle;identity=('{0}:{1}' -f $p[0].Id,$p[0].StartTime.ToFileTimeUtc());responding=$p[0].Responding}|ConvertTo-Json -Compress}"
    try:
        r=subprocess.run(["powershell","-NoProfile","-Command",cmd],capture_output=True,text=True,encoding="utf-8",timeout=8)
        return json.loads(r.stdout) if r.returncode==0 and r.stdout.strip() else {}
    except (OSError,ValueError,subprocess.SubprocessError):
        return {}

def live_project_problem(project, receipt, observed):
    if not observed.get("responding") or not observed.get("identity"):
        return "iClone live session unavailable or not responding"
    if not expected_live_title(project, observed.get("title","")):
        return "wrong live project: "+observed.get("title","")
    if receipt and receipt.get("identity")!=observed["identity"]:
        return "iClone restarted; old live QA is not proof of restored work"
    return ""
