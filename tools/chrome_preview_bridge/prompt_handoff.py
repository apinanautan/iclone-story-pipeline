"""Generate copy-only prompts from current project data."""
from pathlib import Path
import json,re,sys
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/"scripts"))
from workflow_state import active_context
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
ใช้มาตรฐานคุณภาพเดียวกันทั้งเริ่มเรื่อง ทำต่อ และ Sleep Mode; เฉพาะการอนุมัติและการเปลี่ยนแชตเท่านั้นที่ต่างกัน โหมดปกติรอคำอนุมัติจริงก่อนเรนเดอร์ Sleep Mode ใช้สิทธิ์ที่ผู้ใช้เปิดและ gate ที่ runtime รองรับเท่านั้น ห้ามเปิด Sleep เอง เซฟผ่านเมนู File โดยไม่เปิดซ้ำ ตรวจวิดีโอและเสียงจริงก่อนนับว่าเสร็จ ไม่เผยแพร่หรือเขียนทับงานเดิมโดยไม่ได้รับอนุญาต
ลงมือทำต่อจริงตามขั้นที่ได้รับอนุญาต ไม่หยุดเพียงรายงาน ข้อความติดตามนี้เป็นคำสั่งให้ AI ลงมือทำงานต่อเองตามสิทธิ์และขอบเขตที่ผู้ใช้ให้ไว้ ไม่ใช่คำสั่งให้ผู้ใช้ลงมือแทน ห้ามโยนคำสั่ง CLI/PowerShell/Python การพิมพ์ข้อความ การกดปุ่ม หรือขั้นตอนแก้ไขกลับไปให้ผู้ใช้ทำ หากมีเครื่องมือที่ทำได้ ให้เรียกใช้เอง ตรวจผลจริง แล้วทำขั้นถัดไปทันที ไม่ต้องขอให้ผู้ใช้พิมพ์ ลองใหม่ หรืออนุญาตซ้ำสำหรับการแก้ไขและลองใหม่ที่อยู่ในขอบเขตเดิม เมื่อเจอข้อผิดพลาดให้แก้ต้นเหตุหรือเลือกวิธีที่ได้รับอนุญาตแตกต่างจากเดิมก่อนลองใหม่ ไม่วนคำสั่งเดิมที่ไม่เกิดผล ขอผู้ใช้เฉพาะการอนุมัติที่จำเป็นจริง การให้สิทธิ์ที่เครื่องมือกำหนด หรือข้อมูลที่หาเองไม่ได้; หากทำไม่ได้จริงให้แจ้งข้อจำกัดที่พิสูจน์แล้ว ไม่อ้างว่างานสำเร็จ รักษาข้อมูลและความปลอดภัยของเครื่อง ไม่เปิดเผยคีย์ รหัสผ่าน หรือข้อมูลเรื่องอื่น"""
FOCUS="หลักทำงานแบบเดินหน้า: ขั้นตอนที่ลงมือเสร็จและตรวจผ่านแล้วถือว่าจบ ให้เก็บผลงานและหลักฐานเดิม ห้ามย้อนทำซ้ำ เซฟซ้ำ เรนเดอร์ซ้ำ หรือรีเซ็ตสถานะผ่านเพื่อเริ่มใหม่โดยไม่มีเหตุผลจากหลักฐานจริง. เมื่อพบข้อผิดพลาด ให้ระบุจุดที่เสียจากผลจริง แก้เฉพาะจุดนั้นและตรวจซ้ำเฉพาะส่วนที่ได้รับผลกระทบโดยตรงตาม dependency ของ validator. รักษาส่วนอื่นที่ผ่านแล้ว ไม่รื้อทั้งงานหรือย้อนท่อนเก่า. เมื่อแก้ผ่านให้เดินหน้าจากขั้นที่ยังไม่เสร็จทันที. หากผู้ใช้สั่งเปลี่ยนงานให้ยึดคำสั่งล่าสุด ห้ามปลอมผลผ่านหรือข้ามจุดอนุมัติจริง."

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
def historical_part_line(line):
    # Old examples and one-off scripts are not production rules for a new story.
    return bool(re.search(r"(?i)(?:ท่อน|คลิป|part)[ _-]*\d+(?:\.\d+)?(?!\d)|\bic8_part\d+(?:_|\.py\b)",line))


def tool_guide(base,story,other=None):
    """Shared, current, reusable tool guide. Both modes get identical instructions."""
    old=tuple(p.stem for p in (base/"stories").glob("*.json") if not p.stem.startswith("_"))
    # Avoid stale scene-specific examples and credential-looking lines in skill excerpts.
    def reusable(s):
        return "\n".join(line for line in s.splitlines()
            if not historical_part_line(line)
            and not any(x in line for x in old)
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

def build(kind,base=BASE,target=None):
    base=Path(base)
    if kind=="continue":
        return (
            "โหมดทำงานต่อ — คำสั่งกลางสำหรับทุกเรื่องและทุกท่อน\n"
            "อ่านคำสั่งล่าสุดของผู้ใช้ ตรวจสถานะจริงจาก Ai-iclone status และ story spec/part spec ของงานที่กำลังทำก่อนลงมือ "
            "ไม่กำหนดหรือฝังชื่อเรื่อง หมายเลขท่อน จำนวนท่อน หรือสถานะเก่าลงในคำสั่งนี้ "
            "ใช้ลำดับงานตามแผนจริงและเริ่มจากขั้นแรกที่ยังไม่ผ่านของงานปัจจุบัน "
            "ถ้าผู้ใช้เริ่มท่อนใหม่แล้ว ให้ทำท่อนใหม่ ไม่ย้อนกลับไปผลิตท่อนก่อนหน้า "
            "ถ้างานปัจจุบันเสร็จครบแล้ว ให้จบงานนั้นและดำเนินงานถัดไปตามขอบเขตที่ผู้ใช้อนุญาต ไม่ย้อนผลิตซ้ำ.\n\n"
            +FOCUS+"\n\n"+RULES+
            "\n\nตรวจเครื่องมือที่มีอยู่จริง อ่าน Script Catalog และ rules ของขั้นปัจจุบัน ใช้ Preview ควบคุมลำดับงาน. "
            "ใช้ watcher/RLPy/Qt หรือ UI Automation แบบเจาะจงหน้าต่างก่อนเมาส์จริง. "
            "ตรวจการผูกแชตสำหรับส่งภาพจาก /status ของ Relay; marker ของ Prompt ที่ผู้ใช้ส่งจริงใช้ผูกแชตอัตโนมัติตามเรื่องที่เปิดอยู่จริง "
            "ไม่ต้องให้ผู้ใช้พิมพ์หรือกดซ้ำ. ตรวจภาพจริงและใบตอบรับ sent; ใช้ capture_preview.py --send หรือ queue_preview.py ตามคู่มือ "
            "ห้ามส่งซ้ำเมื่อมีภาพค้างหรือยังตรวจใบตอบรับไม่ได้. รักษาข้อจำกัดการเซฟและการอนุมัติจริง. "
            "ไม่คัดลอกประวัติหรือสถานะจากงานเก่ามาเป็นคำสั่ง."
        )
    now=active_context(base)

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
            if historical_part_line(line):continue
            entries.append(name+" — "+cols[2].strip())
    intro="ทุกเรื่องใช้กฎกลางเดียวกัน แต่จำนวนท่อน ชื่อ ลำดับ และเนื้อหาอ่านจาก story spec ของเรื่องนั้นจริง ไม่ใช้ตัวอย่างหรือหมายเลขท่อนจากเรื่องอื่นเป็นข้อบังคับ. ยึดเป้าหมายล่าสุดที่ผู้ใช้ระบุจริง ไม่ใช้สถานะการรันเก่ามาเลือกงานใหม่ ไม่ย้อนทำงานเดิมโดยพลการ. หากข้อมูลขัดกันให้ตรวจและแก้ต้นเหตุโดยรักษาข้อจำกัดและการอนุมัติ.\n\n"+RULES+"\n\nInstalled Pipeline: "+installed+"\nSkills: "+", ".join(skills)+"\nดัชนีสคริปต์ (ตรวจ signature ก่อนใช้):\n"+"\n".join(entries)
    intro+="\nProject root on current machine: "+str(base.resolve())+"\nให้เริ่มจากโปรเจกต์ที่ตรวจพบจริง ไม่เดา path จากเครื่องอื่น; ตรวจว่าปลั๊กอิน GPT และ Dino Bot Tunnel พร้อมใช้งาน แล้วเรียกเครื่องมือที่มีอยู่ตามลำดับงาน."
    if other:
        intro+="\nAvailable release (not automatically installed): "+released+" "+link+"\nReviewed source: "+str(other.resolve())
    # Automatically discover migration and update handbooks. Do not embed private project state in new mode.
    handoffs=sorted(p.name for p in (base/"docs").glob("HANDOFF_*.md") if p.name.startswith("HANDOFF_CINEMATIC") or p.name.startswith("HANDOFF_RELEASE"))
    if handoffs:
        intro+="\nคู่มือย้ายรุ่นที่ระบบพบเอง: "+", ".join("docs/"+p for p in handoffs)+" — อ่านและทำตามเองเมื่อรุ่นที่ติดตั้งต่างจากรุ่นที่เผยแพร่; ไม่ให้ผู้ใช้ต้องส่งคำสั่งซ้ำ"
    if kind=="sleep":
        if not isinstance(story,str) or not story or not re.fullmatch(r"\d+(?:\.\d+)?",str(part)):raise ValueError("invalid target")
        target_header=(
            "คำสั่งเริ่มท่อนเป้าหมาย — เรื่อง "+story+" | ท่อน "+str(part)+"\n"
            "ทำเฉพาะท่อนนี้เท่านั้น ตั้งแต่คำสั่งแรก จนกว่าจะถึงจุดตรวจ/อนุมัติของท่อนนี้ "
            "ห้ามย้อนกลับไปเซฟ เรนเดอร์ ซ่อม หรือทำ QA ท่อนก่อนหน้าโดยพลการ แม้สถานะเก่าในระบบจะยังค้าง "
            "ท่อนก่อนหน้าใช้เป็นไฟล์ต้นทางแบบอ่านอย่างเดียวเท่านั้น ไม่ต้องตรวจเสร็จซ้ำ. "
            "ถ้าเป้าหมายปัจจุบันต่างจากท่อนนี้ ให้เลือกด้วย Ai-iclone use "+json.dumps(story,ensure_ascii=False)+" "+str(part)+" แล้วตรวจ status ว่าตรงกัน. "
            "ถ้าฉากที่เปิดไม่ใช่ท่อนนี้ ให้ใช้ขั้น open ของ Preview เพื่อเปิด/สร้างท่อนนี้ตามสเปก; ห้ามเขียนทับต้นฉบับหรือทิ้งงานที่ยังไม่เซฟ. "
            "หากติด dependency ให้รายงานและแก้เฉพาะ dependency ที่จำเป็น ไม่ย้อนผลิตท่อนเก่า. "
            "ทำขั้นแรกที่ยังไม่ผ่านของท่อนเป้าหมายต่อทันที. ห้ามข้ามการตรวจและอนุมัติ.\n"
            "ส่งภาพเป็นส่วนบังคับของ QA: ตรวจ /status ของ Relay ว่าผูกแชตนี้จริงก่อนสร้างภาพ; "
            "เมื่อใช้ Prompt ส่งต่อที่มี handoff marker ส่วนขยายจะผูกแชตจากข้อความผู้ใช้ที่โพสต์จริงโดยอัตโนมัติ. "
            "ถ้ายังไม่ผูก ให้ตรวจและใช้ปุ่มผูกแชตนี้ ห้ามเดา URL. "
            "จับภาพหน้าต่างท่อนปัจจุบันด้วย py -3 -B tools/chrome_preview_bridge/capture_preview.py --send; "
            "ภาพกล้องจากขั้น cams จะเข้าคิวเองผ่าน queue_preview.py. ถ้าสร้างภาพก่อนผูก ให้ใช้ queue_preview.py กับ JPEG สดที่ตรวจตรงท่อนแล้วโดยไม่สร้างกล้องซ้ำ. "
            "ตรวจ job.json และใบตอบรับ sent; ห้ามส่งภาพซ้ำถ้า pending/claimed/needs_review. ตรวจภาพจริงในแชตก่อน QA. "
            "ควบคุมผ่าน watcher/RLPy/Qt หรือ UI Automation แบบเจาะจงหน้าต่างก่อนใช้เมาส์จริง; "
            "ไม่แย่งเมาส์เมื่อผู้ใช้กำลังทำงาน.\n\n")
        intro=target_header+intro
    intro+=tool_guide(base,story,other)
    if kind=="new":
        return intro+"""\n\nโหมดเริ่มเรื่องใหม่: ไม่นำตัวละคร บท หรือความคืบหน้าเรื่องเดิมมาใช้. อ่านชื่อเรื่องใหม่ บท เสียง และ assets ที่ผู้ใช้ระบุ ถ้าขาดข้อมูลจำเป็นจึงถาม. ตรวจไม่มีงานอื่นรันก่อนสลับเรื่อง. สร้าง story spec ใหม่และอัปเดต CURRENT_STORY.md ให้เหลือเรื่องเดียว. วิเคราะห์บทและเสียงของเรื่องนี้เพื่อกำหนดจำนวนท่อน ช่วงเวลา และลำดับเหตุการณ์จากข้อมูลจริงเท่านั้น ไม่กำหนดจำนวน เลขท่อน หรือรูปแบบท่อนย่อยล่วงหน้า. เริ่มจากรายการแรกในแผนที่อนุมัติ ตรวจและรออนุมัติตาม gate ของแต่ละรายการ แล้วดำเนินรายการถัดไปตามแผนจนจบ. ห้ามเปิดเรื่องเก่าที่ส่งเสร็จแล้วกลับมาแก้."""
    if kind not in ("continue","sleep"):raise ValueError("unknown mode")
    if kind=="sleep":
        intro+="\nSLEEP MODE: ผู้ใช้เปิดโหมดทำทุกท่อนที่อนุมัติแล้ว. ทำเฉพาะท่อน "+str(part)+" ของเรื่องนี้. ใช้ Ai-iclone do, scene_review, prop_review, camera_replan, editorial_review และ final_review. ตรวจจริงทุกขั้น; ใช้ sleep-approve เท่านั้นหลัง QA ผ่าน ไม่ปลอมคำผู้ใช้. เซฟผ่านเมนู File โดยไม่เปิดซ้ำ ตามขั้น ready. ห้ามเปลี่ยนท่อนเอง; ส่วนขยายจะสร้างแชตใหม่หลัง final_review. ห้ามส่ง Drive อัตโนมัติ. เมื่อเสร็จจริงให้หยุดรอ handoff. หากติดปัญหาให้แก้สาเหตุ ห้ามสร้างหลักฐานเท็จ. อ่าน Skill cinematic-direction และ blender-prop-production."
    if not isinstance(story,str) or not story or any(c in story for c in '/\\:*?"<>|') or story in ('.','..'):raise ValueError("no current story")
    data=load(base/"stories"/(story+".json"))
    keys=("name","parts","folder","script_docx","script_split","master_audio","audio_dir","save_dir","video_dir","publish_dir","teacher_range","characters","locations","scenes")
    meta={k:data[k] for k in keys if k in data}
    statuses=[]
    for p in sorted((base/"progress").glob(story+"_*.json")):
        if not re.fullmatch(re.escape(story)+r"_\d+(?:\.\d+)?\.json",p.name):continue
        if p.stem[len(story)+1:]!=str(part):continue
        d=load(p);statuses.append({"part":p.stem[len(story)+1:],"steps_done":list(d.get("steps_done",{})),"approved":bool(d.get("ok",{}).get("step5"))})
    spec=load(base/"parts"/(story+"_"+str(part)+".json")) if re.fullmatch(r"\d+(?:\.\d+)?",str(part)) else {}
    details={k:spec[k] for k in ("story","part","from","project","video","wav","shots","lines","cast","props","scene","face_refinement") if k in spec}
    return intro+"\n\nโหมดทำเรื่องเดิมต่อ — สถานะสดจากเครื่อง:\n"+json.dumps(clean({"now":now,"story":meta,"progress":statuses,"current_part_spec":details}),ensure_ascii=False,indent=2)+"""\n\nอ่าน story spec และ part spec ล่าสุดซ้ำ ตรวจไฟล์วิดีโอและงานที่กำลังรัน. หากคลิปปัจจุบันยังไม่ผ่าน ให้ทำต่อจากขั้นแรกที่ยังไม่เสร็จ ไม่รันซ้ำ. เมื่อผู้ใช้เลือกงานใหม่อย่างชัดเจน ให้ยึดงานนั้น ไม่ย้อนทำงานเดิมเพราะสถานะค้าง; หากมีข้อจำกัดการเปิดทับฉากที่ยังไม่ได้เซฟ ให้รายงานเฉพาะข้อจำกัดนั้น รักษาความต่อเนื่องจากโปรเจกต์ก่อนหน้า. Sleep Mode: ส่วนขยายเป็นผู้เปลี่ยนท่อนเท่านั้น; โหมดปกติยึดท่อนเป้าหมายที่ระบุอย่างเด็ดขาด. วางแผนละเอียดและรักษา gate จริงตามโหมดที่ได้รับอนุญาต."""
