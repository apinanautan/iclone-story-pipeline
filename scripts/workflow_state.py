"""Pure workflow invalidation rules; no GUI or project side effects."""
def invalidated_steps(step, order):
    after = order[order.index(step) + 1:] if step in order and not step.endswith("check") else []
    if step == "sound":
        # Replacing audio needs fresh lip sync and delivery validation, not pose.
        after = [k for k in after if k in ("lip","scene_review","prop_review","camera_replan","cams","cam_check","motion_check","light_check","face_check","editorial_review","switch","ready","render","video_check","final_review")]
    if step == "lip":
        after = [k for k in after if k in ("ready", "render", "video_check")]
    if step == "render":
        after = ["video_check","final_review"]
    if step == "video_check": after=["final_review"]
    if step in ("cam_check","motion_check","light_check","face_check"): after=order[order.index(step)+1:]
    if step == "lip": after=[k for k in order[order.index(step)+1:]]
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
