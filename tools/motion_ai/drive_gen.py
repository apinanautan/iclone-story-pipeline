# Blender 5.3 GUI driver: install add-on, start companion, generate one Kimodo motion, export FBX, log, quit.
import bpy, os, sys, json, time, traceback, glob
ROOT = r"C:\MotionAI"
APP = sorted(glob.glob(ROOT + r"\MotionAI_Windows_Companion-*"))[-1]   # set up by install.ps1
ZIP = sorted(glob.glob(ROOT + r"_dl	oyxyz_motion_ai_tool-*-blender-addon.zip"))[-1]   # downloaded by install.ps1
CFG = json.load(open(ROOT + r"\gen.json", encoding="utf-8"))   # {"prompt":..., "seconds":..., "out":...}
LOG = ROOT + r"\gen_log.txt"
def log(s):
    open(LOG, "a", encoding="utf-8").write(time.strftime("%H:%M:%S ") + str(s) + "\n")

st = {"step": "launch", "t": time.time()}

def tick():
    try:
        import toyxyz_motion_ai_tool as M
        from toyxyz_motion_ai_tool import agent_commands as A, client as C
        ctx = bpy.context
        s = st["step"]
        if s == "launch":
            bpy.ops.toyxyz_motion_ai_tool.launch_app(); st.update(step="wait_conn", t=time.time()); log("launch")
        elif s == "wait_conn":
            if C.state.get("connected"):
                fps = 30; ctx.scene.render.fps = fps
                a = A.actor_add(ctx); log(("actor", a))
                bl = A.actor_data(ctx, None).blocks
                kw = dict(start=1, end=1 + int(CFG["seconds"] * fps), model="kimodo", prompt=CFG["prompt"])
                b = A.block_update(ctx, bl[0].uid, **kw) if len(bl) else A.block_add(ctx, **kw); log(("block", b))
                st["block"] = b; st.update(step="gen", t=time.time())
            elif time.time() - st["t"] > 600: log("TIMEOUT connect " + C.state.get("message", "")); return quit_()
        elif s == "gen":
            log(("generate", A.generate(ctx))); st.update(step="wait_gen", t=time.time())
        elif s == "wait_gen":
            j = A.job_info(ctx.scene)
            if int(time.time()) % 15 == 0: log(("job", j.get("status"), j.get("progress"), j.get("stage"), j.get("message")))
            if j.get("status") == "succeeded" and not j.get("busy"):
                st.update(step="export", t=time.time())
            elif j.get("status") in ("failed", "error", "cancelled") or time.time() - st["t"] > 1800:
                log(("FAILED", j)); return quit_()
        elif s == "export":
            r = A.export_fbx(ctx, CFG["out"], overwrite=True); log(("export", r))
            bpy.ops.wm.save_as_mainfile(filepath=CFG["out"].replace(".fbx", ".blend"))
            log("DONE"); return quit_()
    except Exception:
        log("ERROR " + traceback.format_exc()); return quit_()
    return 1.0

def quit_():
    try:
        from toyxyz_motion_ai_tool import client as C
        C.commands.put(("shutdown", None, None)); time.sleep(2)
    except Exception: pass
    bpy.ops.wm.quit_blender()
    return None

def setup():
    try:
        import addon_utils
        if not any(m.__name__ == "toyxyz_motion_ai_tool" for m in addon_utils.modules()):
            bpy.ops.preferences.addon_install(filepath=ZIP, overwrite=True)
        addon_utils.enable("toyxyz_motion_ai_tool", default_set=True, persistent=True)
        bpy.context.preferences.addons["toyxyz_motion_ai_tool"].preferences.runtime_root = APP
        bpy.ops.wm.save_userpref()
        log("addon ready")
        bpy.app.timers.register(tick, first_interval=2.0)
    except Exception:
        log("ERROR setup " + traceback.format_exc()); quit_()
    return None

open(LOG, "w").close()
bpy.app.timers.register(setup, first_interval=3.0)
