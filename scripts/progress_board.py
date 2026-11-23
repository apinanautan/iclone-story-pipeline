# -*- coding: utf-8 -*-
"""Step board for one story part: green tick = condition met (checked from real files), grey = not yet.

Two boxes: (A) story plan, done once and stays ticked; (B) the current part's loop, fresh for every part
(state is per part, so starting part N+1 starts with an empty box B). Current part = first part with no final video.
python scripts/progress_board.py <story> [N]            -> writes docs/progress.html (reloads itself every 10 s)
python scripts/progress_board.py <story> plan ok        -> user approved the story plan (box A)
python scripts/progress_board.py <story> <N> ok <key>   -> tick a step that needs the user's word (step0 step1 step5 step7 step9)
python scripts/progress_board.py <story> <N> order "<text>"   -> add a user order to track
python scripts/progress_board.py <story> <N> done <i>   -> mark order i (1-based) done
State (user approvals + orders) lives in progress/<story>_<N>.json.
"""
import html, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from paths import expand  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import ffmpeg as _ff
FFPROBE = _ff("ffprobe")


def load(p, default):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return default


def video_ok(p):
    try:
        out = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(p)],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        return out.startswith("1920,1080,60/1"), out
    except Exception as e:
        return False, str(e)


def steps(story, n, st):
    ok = st.get("ok", {})
    s = load(ROOT / "stories" / f"{story}.json", {})
    parts = s.get("parts", [])
    part = next((p for p in (parts.values() if isinstance(parts, dict) else parts) if str(p.get("n")) == str(n)), {})
    spec_p = ROOT / "parts" / f"{story}_{n}.json"
    spec = load(spec_p, {})
    wav = Path(expand(spec.get("wav") or f"{{DESKTOP}}/{story}/เสียงที่ตัดแล้ว/ท่อน{n}.wav"))
    final_proj = Path(expand(f"{{SAVE}}/{story}/ท่อน{n}.iProject"))
    draft = Path(expand(spec["project"])) if spec.get("project") else None
    final_vid = Path(expand(f"{{VIDEO}}/{story}/{n}.mp4"))
    vok, vinfo = video_ok(final_vid) if final_vid.exists() else (False, "ยังไม่มีไฟล์")
    rows = [
        ("0", "อ่านกฎและไฟล์ทั้งหมด", [("AI อ่านครบแล้ว (ผู้ใช้/AI ติ๊ก)", ok.get("step0"))]),
        ("1", "ข้อมูลเรื่องและแผน", [
            ("มีเรื่องใน stories/", bool(part)),
            ("มีแผนของท่อน", bool(part.get("plan"))),
            ("ผู้ใช้ตอบ 'โอเค'", ok.get("step1"))]),
        ("2", "ตัดเสียงและถอดคำ", [
            (f"มีไฟล์เสียง {wav.name}", wav.exists()),
            ("มีไฟล์เวลา .json คู่เสียง", wav.with_suffix(".json").exists()),
            ("ใส่ transcript ใน story.json แล้ว", bool(part.get("transcript")))]),
        ("3", "เขียน spec ท่อน", [
            (f"มี {spec_p.name}", spec_p.exists()),
            (f"มีช็อตกล้อง ({len(spec.get('shots', []))})", bool(spec.get("shots"))),
            ("มีนักแสดง (cast)", bool(spec.get("cast")))]),
        ("4", "สร้างงานใน iClone", [("มีไฟล์โปรเจกต์ที่เซฟไว้", bool(draft and draft.exists()) or final_proj.exists())]),
        ("5", "ตรวจภาพนิ่ง", [("ผู้ใช้บอก 'ผ่าน'", ok.get("step5"))]),
        ("6", "ลิปซิงก์", [("ไม่มีบทพูด (บรรยายล้วน) หรือทำแล้ว",
                           all(l.get("who") == "บรรยาย" for l in spec.get("lines", [])) or ok.get("step6"))]),
        ("7", "เซฟไฟล์จริงและให้ผู้ใช้ดู", [(f"มี {final_proj.name}", final_proj.exists()), ("ผู้ใช้ดูแล้ว", ok.get("step7"))]),
        ("8", "เรนเดอร์", [(f"มี {final_vid.name}", final_vid.exists()), (f"1920x1080 60fps ({vinfo})", vok)]),
        ("9", "ปิดงานท่อน", [("ผู้ใช้ยืนยันจบท่อน", ok.get("step9"))]),
    ]
    return rows


def story_rows(story, sst):
    s = load(ROOT / "stories" / f"{story}.json", {})
    ex = lambda k: bool(s.get(k)) and Path(expand(s[k])).exists()
    chars = s.get("characters", {})
    scenes = s.get("scenes", {})
    miss_av = [c for c, v in chars.items() if not (v.get("avatar") and Path(expand(v["avatar"])).exists())]
    miss_sc = [c for c, v in scenes.items() if not (v.get("file") and Path(expand(v["file"])).exists())]
    sp = [x for v in scenes.values() for x in list((v.get("spots") or {}).values()) + list((v.get("cams") or {}).values())
          if isinstance(x, dict)]
    parts = s.get("parts", [])
    dirs = [("โฟลเดอร์เรื่อง (ไดรฟ์)", "folder"), ("โฟลเดอร์เสียงที่ตัดแล้ว", "audio_dir"),
            ("โฟลเดอร์เซฟโปรเจกต์", "save_dir"), ("โฟลเดอร์วิดีโอ", "video_dir")]
    return [
        ("A0", "สร้างโฟลเดอร์", [(t + (f" — {expand(s[k])}" if s.get(k) else ""), ex(k)) for t, k in dirs]),
        ("A1", "ไฟล์เรื่องและต้นฉบับ", [(f"มี stories/{story}.json", bool(s)), ("มีบท .docx", ex("script_docx")),
                                     ("มีเสียงเต็ม", ex("master_audio"))]),
        ("A2", "วางแผนแบ่งท่อน", [(f"แบ่งแล้ว {len(parts)} ท่อน", bool(parts)),
                                  ("ทุกท่อนมีช่วงเวลาและเนื้อหา", bool(parts) and all(p.get("master") and p.get("content") for p in parts))]),
        ("A3", "ตัวละคร", [(f"มี {len(chars)} ตัว", bool(chars)),
                          ("ไฟล์ avatar ครบ" + (f" (ขาด: {', '.join(miss_av)})" if miss_av else ""), bool(chars) and not miss_av)]),
        ("A4", "ฉาก", [(f"มี {len(scenes)} ฉาก", bool(scenes)),
                      ("ไฟล์ฉากครบ" + (f" (ขาด: {', '.join(miss_sc)})" if miss_sc else ""), bool(scenes) and not miss_sc),
                      (f"จุดยืน/กล้องอนุมัติแล้ว ({sum(bool(x.get('approved')) for x in sp)}/{len(sp)})",
                       bool(sp) and all(x.get("approved") for x in sp))]),
        ("A5", "ผู้ใช้อนุมัติแผนเรื่อง", [("ผู้ใช้ตอบ 'โอเค'", sst.get("ok", {}).get("plan"))]),
    ], [str(p.get("n")) for p in parts]


def box(rows, cur):
    h = []
    for i, (num, title, checks) in enumerate(rows):
        done = all(c for _, c in checks)
        cls = "done" if done else ("cur" if i == cur else "todo")
        items = "".join(f'<li class="{"y" if c else "n"}">{"✔" if c else "○"} {html.escape(t)}</li>' for t, c in checks)
        lab = num if num.startswith("A") else f"สเต็ป {num}"
        h.append(f'<div class="step {cls}"><div class="hd"><span class="b">{"✔" if done else num}</span>'
                 f'{lab} — {html.escape(title)}</div><ul>{items}</ul></div>')
    return "".join(h)


def render(story, n, st, sst, part_ns):
    arows, _ = story_rows(story, sst)
    acur = next((i for i, r in enumerate(arows) if not all(c for _, c in r[2])), None)
    adone = sum(all(c for _, c in r[2]) for r in arows)
    chips = "".join(f'<span class="chip {"cd" if Path(expand(f"{{VIDEO}}/{story}/{p}.mp4")).exists() else ("cc" if p == str(n) else "")}">ท่อน {p}</span>'
                    for p in part_ns)
    rows = steps(story, n, st)
    cur = next((i for i, r in enumerate(rows) if not all(c for _, c in r[2])), None)
    orders = "".join(f'<li class="{"y" if o.get("done") else "n"}">{"✔" if o.get("done") else "○"} {i}. {html.escape(o["text"])}</li>'
                     for i, o in enumerate(st.get("orders", []), 1)) or '<li class="n">ยังไม่มี</li>'
    ndone = sum(all(c for _, c in r[2]) for r in rows)
    return f"""<!doctype html><html lang="th"><head><meta charset="utf-8"><meta http-equiv="refresh" content="10">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>ความคืบหน้า</title><style>
body{{font-family:Tahoma,sans-serif;background:#111;color:#ddd;margin:0;padding:16px;max-width:760px}}
h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#888;margin-bottom:14px;font-size:13px}}
.bar{{height:10px;background:#333;border-radius:5px;margin-bottom:16px}}.bar i{{display:block;height:100%;background:#2ea043;border-radius:5px;width:{ndone*10}%}}
.step{{border:1px solid #333;border-radius:8px;padding:10px 12px;margin:8px 0}}
.done{{border-color:#2ea043;background:#0f2a17}} .cur{{border-color:#d29922;background:#2a220f}}
.hd{{font-weight:bold;display:flex;gap:10px;align-items:center}}
.b{{width:26px;height:26px;border-radius:50%;background:#333;display:inline-flex;align-items:center;justify-content:center}}
.done .b{{background:#2ea043;color:#fff}} .cur .b{{background:#d29922;color:#000}}
ul{{margin:6px 0 0 36px;padding:0;list-style:none;font-size:14px}} .y{{color:#56d364}} .n{{color:#999}}
h2{{font-size:16px;margin-top:22px}} .chip{{display:inline-block;padding:3px 10px;margin:2px;border-radius:12px;background:#333;font-size:13px}} .cd{{background:#2ea043;color:#fff}} .cc{{background:#d29922;color:#000}}</style></head><body>
<h1>{html.escape(story)}</h1><div class="sub">อัปเดต {time.strftime('%H:%M:%S')} (รีเฟรชเองทุก 10 วิ)</div>
<h2>ช่วงที่ 1 — วางแผนเรื่อง (ทำครั้งเดียว) · {adone}/{len(arows)}</h2>{box(arows, acur)}
<div>{chips}</div>
<h2>ช่วงที่ 2 — ทำท่อน {n} (ล้างใหม่ทุกท่อน) · {ndone}/10</h2><div class="bar"><i></i></div>{box(rows, cur)}
<h2>สิ่งที่สั่งให้แก้</h2><div class="step"><ul style="margin-left:0">{orders}</ul></div></body></html>"""


def main():
    story = sys.argv[1]
    spp = ROOT / "progress" / f"{story}_plan.json"
    sst = load(spp, {"ok": {}})
    if sys.argv[2:4] == ["plan", "ok"]:
        sst["ok"]["plan"] = True
        spp.parent.mkdir(exist_ok=True)
        spp.write_text(json.dumps(sst, ensure_ascii=False), encoding="utf-8")
    _, part_ns = story_rows(story, sst)
    if len(sys.argv) > 2 and sys.argv[2] != "plan":
        n = sys.argv[2]
    else:
        n = next((p for p in part_ns if not Path(expand(f"{{VIDEO}}/{story}/{p}.mp4")).exists()), part_ns[-1] if part_ns else "1")
    sp = ROOT / "progress" / f"{story}_{n}.json"
    st = load(sp, {"ok": {}, "orders": []})
    if len(sys.argv) > 4 and sys.argv[2] != "plan":
        cmd, arg = sys.argv[3], sys.argv[4]
        if cmd == "ok":
            st["ok"][arg] = True
        elif cmd == "order":
            st["orders"].append({"text": arg, "done": False})
        elif cmd == "done":
            st["orders"][int(arg) - 1]["done"] = True
        sp.parent.mkdir(exist_ok=True)
        sp.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    out = ROOT / "docs" / "progress.html"
    out.write_text(render(story, n, st, sst, part_ns), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
