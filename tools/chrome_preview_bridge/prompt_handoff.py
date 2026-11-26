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
RULES="""CC5 / iClone Story Pipeline — คำสั่งเริ่มแชต
ควบคุม Windows ผ่าน Dino Bot Tunnel เท่านั้น. อ่าน AGENTS.md, docs/rules.md, docs/WORKFLOW.md, docs/MASTER_PROMPT.md, docs/SCRIPT_CATALOG.md, docs/CAMERA_GUIDE.md, docs/scene_anchors.md, docs/rlpy_lessons.md, docs/accupose_presets.md, docs/event_clip_workflow.md และ Skills ที่เกี่ยวข้องก่อนทำงาน ตรวจข้อมูล Space/GitHub/ปลั๊กอินที่เกี่ยวข้อง. ยึด progress/now.json และ spec ปัจจุบันเหนือ CURRENT_STORY.md ที่อาจล้าสมัย. ตรวจสคริปต์และ asset ที่มีอยู่ก่อนเขียนใหม่.
อ่านบท DOCX และเสียงจริง ตรวจตัวละคร วัย เสื้อผ้า ผม ฉาก ยุค ความต่อเนื่อง. วางแผนทุกเหตุการณ์อย่างละเอียด: ช่วงเวลาเสียง ผู้พูด จุดยืน การเคลื่อนไหว อารมณ์ ปฏิกิริยา ทิศสายตา props กล้อง แสง คัต. ทำทีละท่อนและทีละเหตุการณ์ ไม่แบ่งคลิปเพียงเพราะเปลี่ยนกล้องหรือผู้พูด. รักษาเสียงต้นฉบับครบ ไม่ตัดขาด ซ้ำ ยืด.
ใช้ Ai-iclone.exe และ flow: plan > audio > check > motion_plan > open > cast > sound > pose > lip (ถ้ามีบทพูด) > scene_review > prop_review > camera_replan > cams > cam_check > motion_check > light_check > face_check > editorial_review > switch > user_ok > ready > render > video_check > final_review. ตรวจภาพจริง แก้จนผ่าน ส่งพรีวิวและรออนุมัติก่อนเซฟ/เรนเดอร์. หลังอนุมัติ File > Save Project และเปิดไฟล์เดิมซ้ำผ่านเมนู ตรวจเวลาเซฟ ชื่อโปรเจกต์ Switch เฟรม 0; รอ texture loading เสร็จ. ตรวจ MP4 จริง ความยาวเท่าเสียง ภาพเคลื่อนไหวทุกคัต สีหน้า ปาก เสียง ก่อนเริ่มคลิปถัดไป. ไม่ข้าม gate หรือปลอมผลตรวจ.
ใช้ Motion Library, motion_pool, AccuPOSE, Gesture, Edit Motion Layer, Blender DataLink, Blender Pose/Rig, RLPy ตามเหมาะสม. ส่ง Motion/Pose ปัจจุบันไป Blender เพื่อแก้กระดูกเมื่อจำเป็น ตรวจ retarget จริง. Gesture อยู่ C:\\Users\\Public\\Documents\\Reallusion\\Reallusion Templates\\Animation\\Gesture; Hold Gently.iHand เป็นตัวอย่างท่ามือ. ถ้าแก้ตำแหน่งเล็กน้อยใช้ Transform/Gizmo โดยตรง ไม่รัน Pose ใหม่ทั้งหมด. จัด grip แล้ว Attach หรือ Link เข้ากระดูกมือ/หัวที่ถูกต้อง รักษาตำแหน่งโลก. ผม prop ไม่กลายเป็น native hair อัตโนมัติ. ถ้า Link/Attach ไม่ได้เพราะ dependency cycle ให้ Modify > Look At > Set Free (weight=0 ไม่พอ); Linkage > Pick Parent > ตัวละคร > เลือก sub-node เช่น CC_Base_R_Hand > Align None. ตรวจตำแหน่งสัมพันธ์ต้น/กลาง/ท้ายและนิ้วสัมผัสจริง. ใช้ head/eye expression แทน Look At target ที่ link กับตัวเอง.
กล้องเน้น MS/MCU/CU 75–150mm และบริบท/พร็อพตามบท เมื่อเหมาะสม หน้าไม่ถูกบัง แสงหน้าไม่ขาว/ดำครึ่งซีก ท่าไม่กระตุกหรือทะลุ สีหน้า สายตา กระพริบตรงบท. ส่งภาพพรีวิวก่อนข้อความติดตาม รอ GPT ตรวจภาพและตอบจบ; tracker 90 วินาที คง busy/draft/preview priority และรหัสหยุด.
ชื่อไฟล์ ท่อนN.M.iProject และ N.M.mp4 หนึ่งไฟล์หลักต่อเหตุการณ์ ไม่สร้างเซฟขยะหรือ backup กระจายในโฟลเดอร์ส่งงาน. ส่งเฉพาะงานจริงที่ผู้ใช้กำหนด ไม่ส่ง JSON/log/catalog/AI reference. เรื่องที่ส่งงานและลง YouTube เรียบร้อย ให้ล้างบริบทและข้อมูลชั่วคราวที่ยืนยันว่าไม่ใช้แล้ว ไม่เก็บข้อมูลเรื่องเก่าปนเรื่องใหม่; รักษาต้นฉบับ ผลงานจริง คลังร่วม และงานกำลังทำ. เก็บบทเรียนทั่วไปและสคริปต์ที่ใช้ซ้ำได้. ห้ามเปลี่ยน Tunnel ID/API Key หรือรีสตาร์ต Windows. อัปเดตความสามารถใหม่ในสคริปต์ กฎ Skills Catalog GitHub และปลั๊กอินที่เกี่ยวข้องโดยไม่เผยแพร่ข้อมูลลับ. ลงมือทำจริง ไม่หยุดแค่รายงาน."""
def tool_guide(base,story):
    """Shared, current, reusable tool guide. Both modes get identical instructions."""
    old=() # reusable handbook only; no private story names
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
    for p in sorted((base/".agents"/"skills").glob("*/SKILL.md")):
        s=reusable(read(p))
        if s:sections.append("\n--- Skill: "+p.parent.name+" ---\n"+s)
    return "\n".join(sections)

def build(kind,base=BASE):
    base=Path(base)
    now=load(base/"progress"/"now.json")
    story=now.get("story");part=now.get("part")
    if kind=="sleep":
        session=load(base/"progress"/"sleep_session.json")
        if not session.get("enabled"):raise ValueError("Sleep Mode not active")
        story=session["story"];part=session["part"];now={"story":story,"part":part,"mode":"sleep"}
    skills=sorted(p.parent.name for p in (base/".agents"/"skills").glob("*/SKILL.md"))
    entries=[]
    for line in read(base/"docs"/"SCRIPT_CATALOG.md").splitlines():
        cols=line.split("|")
        if len(cols)>3 and cols[1].strip().startswith(chr(96)):
            name=cols[1].strip()
            if any(k in name for k in ("part9","part3_")):continue
            entries.append(name+" — "+cols[2].strip())
    intro=RULES+"\n\nPipeline: "+read(base/"VERSION").strip()+"\nSkills: "+", ".join(skills)+"\nดัชนีสคริปต์ (ตรวจ signature ก่อนใช้):\n"+"\n".join(entries)
    intro+="\nProject root on current machine: "+str(base.resolve())+"\nให้เริ่มจากโปรเจกต์ที่ตรวจพบจริง ไม่เดา path จากเครื่องอื่น; ตรวจว่าปลั๊กอิน GPT และ Dino Bot Tunnel พร้อมใช้งาน แล้วเรียกเครื่องมือที่มีอยู่ตามลำดับงาน."
    intro+=tool_guide(base,story)
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
    return intro+"\n\nโหมดทำเรื่องเดิมต่อ — สถานะสดจากเครื่อง:\n"+json.dumps(clean({"now":now,"story":meta,"progress":statuses,"current_part_spec":details}),ensure_ascii=False,indent=2)+"""\n\nอ่าน story spec และ part spec ล่าสุดซ้ำ ตรวจไฟล์วิดีโอและงานที่กำลังรัน. หากคลิปปัจจุบันยังไม่ผ่าน ให้ทำต่อจากขั้นแรกที่ยังไม่เสร็จ ไม่รันซ้ำ. เมื่อท่อนก่อนหน้าผ่าน final_review ครบแล้ว จึงเริ่มท่อนถัดไปจากบท/เสียงที่มีอยู่ รักษาความต่อเนื่องจากโปรเจกต์ก่อนหน้า. Sleep Mode: ส่วนขยายเป็นผู้เปลี่ยนท่อนเท่านั้น; โหมดปกติเปลี่ยนท่อนตามผู้ใช้เมื่อ dependency ผ่าน. วางแผนละเอียดและรักษา gate จริงตามโหมดที่ได้รับอนุญาต."""
