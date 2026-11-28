# -*- coding: utf-8 -*-
"""Offline tests for scripts/ai_iclone.py (no iClone, no real step runs: --dry and fake states)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import ai_iclone as A  # noqa: E402

STORY = "เรื่องทดสอบ"


def fake(monkeypatch, story_states, part_states=None, spec=True):
    monkeypatch.setattr(A, "story_now", lambda: STORY)
    monkeypatch.setattr(A, "part_now", lambda s: "2")
    monkeypatch.setattr(A.P, "story_states", lambda s: story_states)
    monkeypatch.setattr(A.P, "step_states", lambda s, n: (part_states or {}, {}))
    monkeypatch.setattr(A.P, "spec_of", lambda s, n: {"shots": [1]} if spec else None)
    monkeypatch.setattr(A, "sel", lambda: {})
    monkeypatch.setattr(A, "save_sel", lambda d: None)
    import workflow_state   # offline: no live iClone to compare against
    monkeypatch.setattr(workflow_state, "live_project_problem", lambda *a: None)


def all_story_done():
    return {k: ("done", "") for k, _ in A.P.STORY_STEPS}


def test_every_step_has_a_kind():
    assert set(A.PART_KIND) == {k for k, _ in A.P.STEPS}
    assert set(A.STORY_KIND) == {k for k, _ in A.P.STORY_STEPS}


def test_story_stage_comes_first(monkeypatch, capsys):
    ss = all_story_done(); ss["chars"] = ("todo", "")
    fake(monkeypatch, ss)
    assert A.do(dry=True) == 3          # AI work: card, no script
    o = capsys.readouterr().out
    assert "งานของ AI ข้อ chars" in o and "ic8_part.py" not in o


def test_user_step_stops(monkeypatch, capsys):
    ss = all_story_done(); ss["range"] = ("todo", "")
    fake(monkeypatch, ss)
    assert A.do(dry=True) == 2
    assert "STOP" in capsys.readouterr().out


def test_part_script_step_runs_ic8_part(monkeypatch, capsys):
    ps = {k: "done" for k, _ in A.P.STEPS}; ps["open"] = "todo"
    fake(monkeypatch, all_story_done(), ps)
    assert A.do(dry=True) == 0
    o = capsys.readouterr().out
    assert "ic8_part.py" in o and " open" in o and "--dry" in o


def test_render_gets_approved_flag_only_after_user_ok(monkeypatch, capsys):
    ps = {k: "done" for k, _ in A.P.STEPS}; ps["user_ok"] = "todo"; ps["render"] = "todo"
    fake(monkeypatch, all_story_done(), ps)
    assert A.do(dry=True) == 2          # stops at user_ok, never reaches render
    ps["user_ok"] = "done"
    assert A.do(dry=True) == 0
    assert "--approved" in capsys.readouterr().out


def test_two_fails_stop(monkeypatch, capsys):
    ps = {k: "done" for k, _ in A.P.STEPS}; ps["cams"] = "todo"
    fake(monkeypatch, all_story_done(), ps)
    monkeypatch.setattr(A, "fails", lambda step, add=None: 2)
    assert A.do(dry=True) == 2
    assert "ลองทางซ่อมครบแล้ว" in capsys.readouterr().out


def test_plan_complete():
    pc = A.P.plan_complete
    assert not pc(None)
    assert not pc({"lines": [{"who": "?"}], "shots": [1]})
    assert not pc({"lines": [{"who": "แม่"}], "shots": []})
    assert pc({"lines": [{"who": "แม่"}], "shots": [1]})


def test_cards_exist_for_every_step():
    for k in list(A.PART_KIND) + list(A.STORY_KIND):
        assert A.card(k).strip()


def test_clean_jobs_keeps_queue_and_new_files(monkeypatch):
    import tempfile, time as _t
    from pathlib import Path
    d = Path(tempfile.mkdtemp()); old = _t.time() - 5 * 86400
    def mk(rel, age_old):
        f = d / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes(b"x" * 10)
        if age_old: os.utime(f, (old, old))
        return f
    keep = [mk("run/job.py", True), mk("part_cams.jpg", False)]
    gone = [mk("c3_00.png", True), mk("run/old.done", True), mk("backup/a_20261101.iProject", False), mk("qa/x.jpg", True)]
    monkeypatch.setattr(A.P, "J", d)
    b, n = A.P.clean_jobs()
    assert n == 4 and b == 40
    assert all(f.exists() for f in keep) and not any(f.exists() for f in gone)
    assert not (d / "qa").exists()


if __name__ == "__main__":   # no pytest on this PC: tiny stand-ins for monkeypatch / capsys
    import inspect, io, contextlib, traceback

    class MP:
        def __init__(self): self.undo = []
        def setattr(self, o, n, v): self.undo.append((o, n, getattr(o, n))); setattr(o, n, v)
        def restore(self):
            for o, n, v in reversed(self.undo): setattr(o, n, v)

    class Cap:
        def __init__(self, buf): self.buf = buf
        def readouterr(self):
            v = self.buf.getvalue(); self.buf.seek(0); self.buf.truncate()
            return type("R", (), {"out": v})()

    bad = 0
    for name, fn in sorted(globals().copy().items()):
        if not name.startswith("test_"): continue
        mp, buf = MP(), io.StringIO()
        args = {"monkeypatch": mp, "capsys": Cap(buf)}
        try:
            with contextlib.redirect_stdout(buf):
                fn(**{a: args[a] for a in inspect.signature(fn).parameters})
            print("ok  ", name)
        except Exception:
            bad += 1; print("FAIL", name); traceback.print_exc()
        finally:
            mp.restore()
    print("%d failed" % bad); sys.exit(1 if bad else 0)
