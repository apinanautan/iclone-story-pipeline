# Ai-iclone

โปรแกรมทำวิดีโอนิทาน 3D จากเสียง ใน iClone 8 ทีละท่อน ให้ AI (Claude, Codex, ...) คุมเป็นขั้นๆ 1 2 3 ...

## ใช้กับ AI
พิมพ์ในแชทของ AI แค่นี้:

> ใช้โปรแกรม `<โฟลเดอร์นี้>\Ai-iclone.exe` ทำเรื่อง <ชื่อ> ท่อน 1

AI รัน `Ai-iclone.exe` (ไม่ใส่อะไร) ครั้งแรกจะได้: โปรแกรมนี้คืออะไร, กฎเหล็ก, คำพูดในแชท -> คำสั่ง,
สถานะทุกข้อ และคำสั่งถัดไป แล้วทำงานด้วย `Ai-iclone.exe do` ทีละข้อจนเจอ STOP

| คำสั่ง | ทำอะไร |
|---|---|
| `Ai-iclone.exe` | คู่มือ + สถานะ + ข้อถัดไป |
| `Ai-iclone.exe do` | ทำข้อถัดไป (โปรแกรมทำ / การ์ดกฎให้ AI เติมไฟล์ / STOP รอผู้ใช้) |
| `Ai-iclone.exe use <เรื่อง> [ท่อน]` | เลือกเรื่อง/ท่อน |
| `Ai-iclone.exe new-story <เรื่อง>` | เรื่องใหม่ |
| `Ai-iclone.exe range 0:00-7:14` | เวลาที่ทำงาน (จากผู้ใช้เท่านั้น) |
| `Ai-iclone.exe approve --said "ผ่าน"` | บันทึกการอนุมัติที่ผู้ใช้พิมพ์ในแชท |
| `Ai-iclone.exe window` | เปิดหน้าต่าง Ai-iclone (สถานะเดียวกัน ให้คนดู/คลิกผ่าน) |
| `Ai-iclone.exe version` | เวอร์ชัน |

## ติดตั้ง = โหลดไฟล์เดียว
1. โหลด `Ai-iclone.exe` จากหน้า Releases เอาไว้ที่ไหนก็ได้ ไม่ต้องแตกไฟล์ ไม่ต้องติดตั้ง ต้องมี Python 3 (`py`) และ iClone 8
2. เปิดครั้งแรก exe โหลดตัวโปรแกรม (สคริปต์ .py, skills, docs) จาก GitHub เองไปไว้ที่ `%LOCALAPPDATA%\Ai-iclone`
3. อัปเดตเอง: ทุกครั้งที่ใช้ (เช็กไม่เกินทุก 10 นาที) ถ้ามี Release ใหม่กว่า จะโหลดมาทับให้เอง หรือสั่ง `Ai-iclone.exe update`
   ข้อมูลงาน (`stories/`, `parts/`, `progress/`) และ `paths.local.json` ไม่ถูกทับ ไม่มีเน็ต = ใช้ตัวที่มีอยู่
4. ใส่ `paths.local.json` (ที่อยู่ไดรฟ์ของเครื่อง ดู `.agents/skills/paths/SKILL.md`) และคัดลอก `stories/` `parts/` จากเครื่องเดิม หรือเริ่มเรื่องใหม่ด้วย `new-story`
5. ใน iClone: Script > Load Python > `scripts/ic8_watch.py` ครั้งเดียวต่อการเปิด iClone

ถ้า exe อยู่ในโฟลเดอร์ที่มี `scripts/` อยู่แล้ว (เช่น git clone) จะใช้โฟลเดอร์นั้นแทน; ถ้าเป็น git clone จะไม่อัปเดตเอง (ใช้ `git pull`)
ออกเวอร์ชันใหม่: แก้ `VERSION`, commit, push, แล้วสร้าง GitHub Release tag `vX.Y.Z` (แนบ `Ai-iclone.exe`; build ด้วย `launcheruild.ps1`)

---

# ChatGPT / MCP: ปุ่มเดียวกับ Ai-iclone (ทำใหม่ 2026-11-22)

`mcp_server/server.py` คือตัวเชื่อมให้ ChatGPT (ผ่าน MyComp Bot ของเครื่องไหนก็ได้ ชื่อเครื่องไม่สำคัญ) หรือโปรแกรม AI ที่รองรับ MCP สั่งงาน Ai-iclone ได้
มี 10 ปุ่ม แต่ละปุ่มเรียกคำสั่ง Ai-iclone หนึ่งคำสั่ง และใช้ได้ทุกท่อน (ของเก่ามีประมาณ 20 ปุ่มตายตัว และหลายปุ่มใช้ได้แค่ท่อน 2):
`status`, `steps`, `rules`, `do_next_step`, `use_part`, `new_story`, `set_range`, `approve`, `clean_temp_files`, `version`

วิธีที่ AI ใช้: เรียก `status` แล้วเรียก `do_next_step` ซ้ำไปเรื่อยๆ ถ้าเจอ STOP ให้บอกผู้ใช้แล้วรอ ปุ่ม `approve` ต้องใส่คำที่ผู้ใช้พิมพ์มาจริงเท่านั้น

สั่งผ่าน MyComp Bot (เครื่องไหนก็ได้) หรือ PowerShell (ครั้งละปุ่ม):

```powershell
py -3 "%USERPROFILE%\Documents\iClone Story Pipeline\mcp_server\server.py" --cli status
py -3 "%USERPROFILE%\Documents\iClone Story Pipeline\mcp_server\server.py" --cli do_next_step "{\"dry\": true}"
```

ถ้าใช้ MCP client แบบ stdio ให้ดูการตั้งค่าที่ `mcp_server/mcp.local.json` ส่วน `--http` เปิดได้แค่ที่ 127.0.0.1:8766 และไม่มีรหัสผ่าน ห้ามเปิดให้เข้าจากอินเทอร์เน็ต

## Optional automatic watcher startup

`mcp_server/openplugin/main.py` is a small iClone OpenPlugin auto-loader. To enable:

1. **Double-click** `mcp_server/install_openplugin.cmd` and approve the Windows administrator/UAC prompt. This copies the bridge to `C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\iCloneStoryBridge\main.py`. If Windows elevation is denied, leave the file staged and start watcher manually.
2. **Do not restart iClone just to test** if the current scene is unsaved. On the *next normal launch*, iClone attempts to initialize the plugin, which starts the existing watcher only when the watcher run directory has no pending `.py` jobs.
3. After launch, inspect `%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\mcp_autostart_status.txt` and run `Ai-iclone status` to check. Installation alone doesn't prove startup worked.

If a pending `.py` job exists at startup, the auto-loader **refuses to start** until the queue is manually reviewed; it does not silently run old jobs. A dangerous stale `clr.py` containing the known `.rlDikPreset` crash-inducing call was preserved under `.unsafe-hold-20261107` during this installation. Do not run it. The read-only scene probe subsequently completed successfully, confirming the watcher and RLPy bridge were operational. The auto-loader installer still needs user-approved UAC because the current remote shell cannot write to Program Files.
