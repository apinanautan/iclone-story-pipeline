"""Generate copy-only prompts from current project data."""
from pathlib import Path
import json,re
BASE=Path(__file__).resolve().parents[2]
def load(p):
    try:return json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError,ValueError):return {}
def read(p):
    try:return p.read_text(encoding="utf-8-sig")
    except OSError:return ""
def clean(v):
    if isinstance(v,dict):return {k:clean(x) for k,x in v.items() if not re.search(r'password|secret|token|api.?key|relay.?key|credential|authorization',k,re.I)}
    if isinstance(v,list):return [clean(x) for x in v]
    return v
RULES="""CC5 / iClone Story Pipeline — คู่มือสดร่วมทุกโหมด
ก่อนเริ่มงานทุกครั้ง ตรวจเวอร์ชันบนเครื่องและ GitHub releases/main รวมถึงปลั๊กอิน iClone Story Operator ล่าสุดจากเครื่องมือที่มีอยู่จริง; ตรวจความต่างระหว่างรุ่นที่ติดตั้งและรุ่นที่เผยแพร่ ไม่ถือว่า release candidate ติดตั้งแล้ว อัปเดตอย่างปลอดภัยตามคำสั่งผู้ใช้และคู่มือ migration ที่พบเอง ไม่ต้องให้ผู้ใช้ส่งชื่อไฟล์หรือชื่อ Skill เพิ่ม ห้าม git reset/pull ทับงานที่แก้ค้างหรือเปลี่ยนรุ่นกลางขั้นที่กำลังรัน ถ้าอัปเดตไม่ได้ให้ใช้ความสามารถที่ตรวจแล้วว่าใช้งานได้ และรายงานข้อจำกัดจริง
อ่าน AGENTS.md, docs/rules.md, docs/WORKFLOW.md, docs/MASTER_PROMPT.md, docs/SCRIPT_CATALOG.md, docs/CAMERA_GUIDE.md และ Skill ล่าสุดตามดัชนีที่สร้างจากไฟล์จริงด้านล่าง รวมถึงคู่มือใหม่ที่ปรากฏ ตรวจ live Preview status/rules ก่อนแต่ละขั้น ยึดสเปกและ progress จริงเหนือบริบทเก่า เลือกสคริปต์ที่มีอยู่ก่อนเขียนใหม่ ไม่มีลำดับขั้นหรือเลนส์ที่ฝังตายตัวใน Prompt; ใช้ validator ของ runtime ที่ตรวจแล้ว
วางแผนบทและเวลาเสียงจริง จัดตัวละครตามวัย เสื้อผ้า ฉาก พร็อพ การแสดง อารมณ์และบทพูด รักษา Project Sound เดิม ไม่ใส่ซ้ำ วางกล้องตามความหมายและฉากจริง ตรวจ motion/face/lip/light/camera และลำดับภาพ ใช้ Blender, DataLink, Motion Library, AccuPOSE, Gesture, Edit Motion Layer และ RLPy ตามความเหมาะสม ตรวจผลจริง ไม่ปลอมหลักฐาน
ใช้มาตรฐานคุณภาพเดียวกันทั้งเริ่มเรื่อง ทำต่อ และ Sleep Mode; เฉพาะการอนุมัติและการเปลี่ยนแชตเท่านั้นที่ต่างกัน โหมดปกติรอคำอนุมัติจริงก่อนเรนเดอร์ Sleep Mode ใช้สิทธิ์ที่ผู้ใช้เปิดและ gate ที่ runtime รองรับเท่านั้น ห้ามเปิด Sleep เอง เซฟและเปิดซ้ำผ่านเมนู File ตรวจวิดีโอและเสียงจริงก่อนนับว่าเสร็จ ไม่เผยแพร่หรือเขียนทับงานเดิมโดยไม่ได้รับอนุญาต
ลงมือทำต่อจริงตามขั้นที่ได้รับอนุญาต ไม่หยุดเพียงรายงาน รักษาข้อมูลและความปลอดภัยของเครื่อง ไม่เปิดเผยคีย์ รหัสผ่าน หรือข้อมูลเรื่องอื่น"""
def release_info(base):
    # Local pointer contains only a path to a reviewed candidate; it is not a runtime switch.
    v=read(base/"VERSION").strip() or "unknown"
    cfg=load(base/"docs"/"prompt_release.local.json")
    other=Path(cfg.get("source","")) if cfg.get("source") else None
    if other and other.is_dir() and (other/"docs"/"CINEMATIC_SLEEP.md").is_file():
        released=read(other/"VERSION").strip()
        def ver(x):return tuple(int(n) for n in re.findall(r"\d+",x)[:3])
        if ver(released)>ver(v):return v,other,released,cfg.get("release","")
    return v,None,"",""
def skill_files(base,other=None):
    result={p.parent.name:p for p in (base/".agents"/"skills").glob("*/SKILL.md")}
    if other:
        # Installed instructions remain authoritative; expose candidate skills separately below.
        for p in (other/".agents"/"skills").glob("*/SKILL.md"):result.setdefault(p.parent.name,p)
    return result
def tool_guide(base,story,other=None):
    """Shared, current, reusable tool guide. Both modes get identical instructions."""
    old=tuple(p.stem for p in (base/"stories").glob("*.json") if not p.stem.startswith("_"))
    # Avoid stale scene-specific examples and credential-looking lines in skill excerpts.
    def reusable(s):
        return "\n".join(line for line in s.splitlines()
            if not any(x in line for x in old)
            and not (story and story in line)
            and not re.search(r'(?i)(?:api.?key|password|secret|token|relay.?key)\s*[:=]|[0-9a-f]{64}|https://chatgpt\.com/.*/?c/',line))
    sections=["\n\n=== คู่มือเครื่องมือร่วม (ใช้ครบทั้งเริ่มใหม่และทำต่อ) ===",
      "ทุกแชตต้องค้นหาและใช้ปลั๊กอิน GPT ของ iClone Story Pipeline, Dino Bot Tunnel และเครื่องมือที่ติดตั้งอยู่จริง ไม่สมมติว่าเครื่องมือไม่มีเพราะแชตใหม่. เปิดโปรเจกต์จริง อ่าน Script Catalog, AGENTS.md และ Rules ของขั้นปัจจุบันก่อนเรียกสคริปต์. ใช้ Preview/CLI ของปลั๊กอินเป็นตัวกำกับงาน; ตรวจคำสั่ง help/rules ของเวอร์ชันปัจจุบันก่อนแก้ไฟล์หรือเรียก API. หากปลั๊กอินไม่พร้อม ให้ตรวจเครื่องมือที่เชื่อมอยู่และใช้ Dino Bot Tunnel เรียก Ai-iclone.exe ตามกฎเดิม ไม่ให้ผู้ใช้สั่งย่อยซ้ำ.",
      "เส้นทางเลือกเครื่องมือ: วางแผน/สถานะ = Ai-iclone.exe และ progress; เสียง = cut_audio/transcribe และ sound/lip; pose = motion_pool, AccuPOSE, Gesture, Edit Motion Layer, Blender DataLink และ RLPy; กล้อง = ic8_cams, contact_sheet, cam_check; สีหน้า/การเคลื่อนไหว = face_check, motion_check, light_check; save/render = ic8_gui และ gate ของ CLI; ส่งภาพ = chrome_preview_bridge; ทดสอบ = watcher, logs และ tests. ค้นสคริปต์ตามหน้าที่ในดัชนีด้านบน อ่าน signature และข้อจำกัดก่อนเรียก.",
      "เครื่องมือที่ชื่อปรากฏในคู่มืออาจยังไม่ติดตั้งหรือยังไม่ผ่านการทดสอบบนเครื่องนี้ ต้องตรวจจริง ไม่กล่าวอ้างว่าใช้งานได้แล้ว. คู่มือขั้นปัจจุบันและคำสั่งล่าสุดของผู้ใช้มีลำดับเหนือข้อความเก่าในเอกสาร."]
    for rel in ("plugin/INSTRUCTIONS.md","docs/CHROME_PREVIEW_GUIDE.md","docs/CINEMATIC_SLEEP.md","docs/accupose_presets.md","docs/rlpy_lessons.md"):
        s=reusable(read(base/rel))
        if s:sections.append("\n--- "+rel+" ---\n"+s)
    for p in sorted(skill_files(base,other).values(),key=lambda p:p.parent.name):
        s=reusable(read(p))
        if s:sections.append("\n--- Skill: "+p.parent.name+" ---\n"+s)
    if other and other.resolve()!=base.resolve():
        sections.append("\n=== คู่มือความสามารถรุ่นเผยแพร่ที่ยังไม่ใช่ runtime ที่ติดตั้ง ===")
        for rel in ("docs/CINEMATIC_SLEEP.md","docs/SCRIPT_CATALOG.md"):
            data=reusable(read(other/rel))
            if data:sections.append("\n--- release "+rel+" ---\n"+data)
        for p in sorted((other/".agents"/"skills").glob("*/SKILL.md")):
            original=base/".agents"/"skills"/p.parent.name/"SKILL.md"
            if original.exists() and read(original)==read(p):continue
            data=reusable(read(p))
            if data:sections.append("\n--- release Skill: "+p.parent.name+" ---\n"+data)
    return "\n".join(sections)

def build(kind,base=BASE):
    base=Path(base)
    now=load(base/"progress"/"now.json")
    story=now.get("story");part=now.get("part")
    if kind=="sleep":
        session=load(base/"progress"/"sleep_session.json")
        if not session.get("enabled") or session.get("phase") not in ("work","handoff"):raise ValueError("Sleep Mode not active")
        story=session["story"];part=session["part"];now={"story":story,"part":part,"mode":"sleep"}
    installed,other,released,link=release_info(base)
    skills=sorted(skill_files(base,other))
    entries=[]
    for line in read(base/"docs"/"SCRIPT_CATALOG.md").splitlines():
        cols=line.split("|")
        if len(cols)>3 and cols[1].strip().startswith(chr(96)):
            name=cols[1].strip()
            if any(k in name for k in ("part9","part3_")):continue
            entries.append(name+" — "+cols[2].strip())
    intro=RULES+"\n\nInstalled Pipeline: "+installed+"\nSkills: "+", ".join(skills)+"\nดัชนีสคริปต์ (ตรวจ signature ก่อนใช้):\n"+"\n".join(entries)
    intro+="\nProject root on current machine: "+str(base.resolve())+"\nให้เริ่มจากโปรเจกต์ที่ตรวจพบจริง ไม่เดา path จากเครื่องอื่น; ตรวจว่าปลั๊กอิน GPT และ Dino Bot Tunnel พร้อมใช้งาน แล้วเรียกเครื่องมือที่มีอยู่ตามลำดับงาน."
    if other:
        intro+="\nAvailable release (not automatically installed): "+released+" "+link+"\nReviewed source: "+str(other.resolve())
    # Automatically discover migration and update handbooks. Do not embed private project state in new mode.
    handoffs=sorted(p.name for p in (base/"docs").glob("HANDOFF_*.md") if p.name.startswith("HANDOFF_CINEMATIC") or p.name.startswith("HANDOFF_RELEASE"))
    if handoffs:
        intro+="\nคู่มือย้ายรุ่นที่ระบบพบเอง: "+", ".join("docs/"+p for p in handoffs)+" — อ่านและทำตามเองเมื่อรุ่นที่ติดตั้งต่างจากรุ่นที่เผยแพร่; ไม่ให้ผู้ใช้ต้องส่งคำสั่งซ้ำ"
    intro+=tool_guide(base,story,other)
    if kind=="new":
        return intro+"""\n\nโหมดเริ่มเรื่องใหม่: ไม่นำตัวละคร บท หรือความคืบหน้าเรื่องเดิมมาใช้. อ่านชื่อเรื่องใหม่ บท เสียง และ assets ที่ผู้ใช้ระบุ ถ้าขาดข้อมูลจำเป็นจึงถาม. ตรวจไม่มีงานอื่นรันก่อนสลับเรื่อง. สร้าง story spec ใหม่และอัปเดต CURRENT_STORY.md ให้เหลือเรื่องเดียว. วางแผนละเอียดทุกท่อนก่อนลงมือ แล้วทำท่อน 1 ทีละเหตุการณ์ 1.1, 1.2 ... ตรวจและรออนุมัติแต่ละคลิป จบและตรวจไฟล์จริงครบทั้งท่อนก่อนเริ่มท่อน 2, 3 ตามลำดับ. ห้ามเปิดเรื่องเก่าที่ส่งเสร็จแล้วกลับมาแก้."""
    if kind not in ("continue","sleep"):raise ValueError("unknown mode")
    if kind=="sleep":
        intro+="\nSLEEP MODE: ผู้ใช้เปิดโหมดทำทุกท่อนที่อนุมัติแล้ว. ทำเฉพาะท่อน "+str(part)+" ของเรื่องนี้. ใช้ Ai-iclone do, scene_review, prop_review, camera_replan, editorial_review และ final_review. ตรวจจริงทุกขั้น; ใช้ sleep-approve เท่านั้นหลัง QA ผ่าน ไม่ปลอมคำผู้ใช้. เปิด/เซฟ/เปิดซ้ำผ่านเมนู File ตามขั้น ready. ห้ามเปลี่ยนท่อนเอง; ส่วนขยายจะสร้างแชตใหม่หลัง final_review. ห้ามส่ง Drive อัตโนมัติ. เมื่อเสร็จจริงให้หยุดรอ handoff. หากติดปัญหาให้แก้สาเหตุ ห้ามสร้างหลักฐานเท็จ. อ่าน Skill cinematic-direction และ blender-prop-production."
    if not isinstance(story,str) or not story or any(c in story for c in '/\\:*?"<>|') or story in ('.','..'):raise ValueError("no current story")
    data=load(base/"stories"/(story+".json"))
    keys=("name","folder","script_docx","script_split","master_audio","audio_dir","save_dir","video_dir","publish_dir","teacher_range","characters","locations","scenes")
    meta={k:data[k] for k in keys if k in data}
    statuses=[]
    for p in sorted((base/"progress").glob(story+"_*.json")):
        if not re.fullmatch(re.escape(story)+r"_\d+(?:\.\d+)?\.json",p.name):continue
        d=load(p);statuses.append({"part":p.stem[len(story)+1:],"steps_done":list(d.get("steps_done",{})),"approved":bool(d.get("ok",{}).get("step5"))})
    spec=load(base/"parts"/(story+"_"+str(part)+".json")) if re.fullmatch(r"\d+(?:\.\d+)?",str(part)) else {}
    details={k:spec[k] for k in ("story","part","from","project","video","wav","shots","lines","cast","props","scene","face_refinement") if k in spec}
    return intro+"\n\nโหมดทำเรื่องเดิมต่อ — สถานะสดจากเครื่อง:\n"+json.dumps(clean({"now":now,"story":meta,"progress":statuses,"current_part_spec":details}),ensure_ascii=False,indent=2)+"""\n\nอ่าน story spec และ part spec ล่าสุดซ้ำ ตรวจไฟล์วิดีโอและงานที่กำลังรัน. หากคลิปปัจจุบันยังไม่ผ่าน ให้ทำต่อจากขั้นแรกที่ยังไม่เสร็จ ไม่รันซ้ำ. เมื่อท่อนก่อนหน้าผ่านการตรวจไฟล์และ gate สุดท้ายของ runtime ที่ใช้งานจริงแล้ว จึงเริ่มท่อนถัดไปจากบท/เสียงที่มีอยู่ รักษาความต่อเนื่องจากโปรเจกต์ก่อนหน้า. Sleep Mode: ส่วนขยายเป็นผู้เปลี่ยนท่อนเท่านั้น; โหมดปกติเปลี่ยนท่อนตามผู้ใช้เมื่อ dependency ผ่าน. วางแผนละเอียดและรักษา gate จริงตามโหมดที่ได้รับอนุญาต."""
