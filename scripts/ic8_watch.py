# Load ONCE per iClone launch (Script > Load Python). Afterwards Claude drops scripts into
#   %LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\run\*.py
# and this timer runs each one inside iClone, then renames it to .done (or .err) and writes <name>.log.
# No more menus / screenshots needed.
import os, glob, traceback, builtins
from PySide2 import QtCore, QtWidgets

# Tells iClone the script targets iClone 8, so Script > Load Python stops showing "not compatible with the current version".
rl_plugin_info = {"ap": "iClone", "ap_version": "8.0"}

RUN = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs", "run")
os.makedirs(RUN, exist_ok=True)


def _tick():
    # processEvents() inside RLPy jobs can re-enter Qt callbacks. Never run a second job.
    if getattr(builtins, "_ic8_job_running", False):
        return
    app = QtWidgets.QApplication.instance()
    if app is None or app.activeModalWidget() is not None:
        return
    for w in app.topLevelWidgets():
        if w.isVisible() and (isinstance(w, QtWidgets.QProgressDialog)
                or "progressdlg" in w.metaObject().className().lower()):
            return
    files = sorted(glob.glob(os.path.join(RUN, "*.py")))
    if not files:
        return
    f = files[0]
    base = f[:-3]
    builtins._ic8_job_running = True
    t.stop()
    try:
        code = open(f, encoding="utf-8").read()
        g = {"__name__": "__main__", "__file__": f}
        exec(compile(code, f, "exec"), g)
        open(base + ".log", "a", encoding="utf-8").write("OK\n")
        os.replace(f, base + ".done")
    except Exception:
        open(base + ".log", "a", encoding="utf-8").write(traceback.format_exc())
        os.replace(f, base + ".err")
    finally:
        builtins._ic8_job_running = False
        t.start(1000)


old = getattr(builtins, "_claude_ic8_timer", None)
if old:
    old.stop()
t = QtCore.QTimer()
t.timeout.connect(_tick)
t.start(1000)
builtins._claude_ic8_timer = t  # keep it alive
open(os.path.join(RUN, "watcher.alive"), "w").write("guard-v2:" + str(os.getpid()))
