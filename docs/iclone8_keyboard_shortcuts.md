# คู่มือคีย์ลัด iClone 8

คู่มือนี้ถอดรายการคีย์ลัดจากหน้าตารางอ้างอิงทางการ 4 หน้า ได้แก่ Global Shortcuts, Shortcuts in Panels, Timeline Shortcuts และ Curve Editor Keyboard Shortcuts ของคู่มือ iClone 8.0 ตรวจเมื่อ 2026-11-15 และเพิ่มการยืนยัน F3 จากคู่มือ iClone 8.7 ไว้ด้วย คำอธิบายภาษาไทยสรุปตามต้นฉบับ ส่วนคีย์ลัดที่เป็นเมาส์/คีย์ผสมก็รวมไว้ด้วย หน้าอื่นในคู่มืออาจกล่าวถึง shortcut เฉพาะขั้นตอน (เช่น F3 เปิด Timeline) แต่ไม่ใช่ตารางอ้างอิงแยกอีกชุด

## วิธีอ่านและเลือกโฟกัส

- คีย์เดี่ยวอย่าง `F`, `A`, `D`, `E`, `I`, `Q`, `R`, `S`, `T`, `V`, `W`, `Z` มีความหมายต่างกันตามโฟกัส เช่น `F` จัดกล้องให้เห็นด้านหน้าวัตถุที่เลือกใน Quick Camera Positioning, เปลี่ยนเป็น Free Camera ใน Motion Director, และอาจเป็นคำสั่งอื่นใน editor panel. อย่ากดคีย์เดี่ยวจนกว่าจะยืนยันแผง/โหมดที่กำลังรับคีย์
- `Ctrl+B` เป็น Isolate Selection ในบริบท viewport แต่เป็น Break คลิปเมื่อ Timeline รับโฟกัส; `Ctrl+Left/Right` ใช้ย้ายวัตถุ/หมุนใน viewport แต่ใช้ไป key ก่อนหน้า/ถัดไปใน Timeline
- คลิกพื้นที่ Timeline หรือใช้ `Shift+F3` ให้ Timeline รับโฟกัสก่อนใช้คำสั่ง Timeline; ถ้าโฟกัสอยู่ในช่องข้อความหรือ dialog ให้คีย์ไปทำงานในช่อง/dialog แทน
- `F3` แสดง/ซ่อน Timeline แต่ `Shift+F3` ย้ายโฟกัสไปยัง Timeline
- คอลัมน์ “คลิกแทน” ระบุแผง/คำสั่งที่ใช้เมาส์ได้ ชื่อเมนูหรือปุ่มบางรายการอาจต่างตาม minor version/ภาษา
- รายการนี้อ้างอิงค่าเริ่มต้นในคู่มือออนไลน์ ไม่ได้ทดสอบกับ iClone ที่ติดตั้งในเครื่องนี้ คีย์อาจถูกแก้ใน Hotkey Manager หรือถูกคีย์บอร์ดเลย์เอาต์ตีความต่างกัน

## Global Shortcuts — คำสั่งทั่วโปรแกรม

| หมวด / คำสั่ง | คีย์ | ใช้ทำอะไร / ใช้เมื่อไร | บริบทและคลิกแทน |
|---|---|---|---|
| File — New Project | `Ctrl+N` | สร้างโปรเจกต์ใหม่ | หน้าต่างหลัก; File > New Project |
| File — Open Project | `Ctrl+O` | เปิดโปรเจกต์ | File > Open Project; ตรวจชื่อไฟล์ก่อนยืนยัน |
| File — Save Project | `Ctrl+S` | บันทึกโปรเจกต์ปัจจุบัน | File > Save Project; ตรวจ path/ไฟล์บนดิสก์ตามกฎโครงการ |
| File — Save Project As | `Ctrl+Shift+S` | บันทึกเป็นไฟล์ใหม่ | File > Save Project As; ตรวจ path ใน dialog |
| File — Import | `Ctrl+I` | เปิดนำเข้าไฟล์ที่รองรับ | File > Import; ต้องเลือกชนิด/แทร็กด้วย UI เอง |
| File — Merge Project | `Ctrl+Shift+I` | รวม objects จาก iProject เข้ามาในโปรเจกต์ปัจจุบัน | File > Merge Project; ตรวจโปรเจกต์ปลายทางก่อน |
| File — Exit | `Alt+F4` | ปิด iClone | File > Exit; ระวัง dialog บันทึกงาน |
| Workspace — Standard | `Ctrl+2` | เลย์เอาต์มาตรฐาน | Workspace menu |
| Workspace — Animation | `Ctrl+3` | เลย์เอาต์เครื่องมือ animation | Workspace menu |
| Workspace — Visual Effects | `Ctrl+4` | เลย์เอาต์ Visual Effects | Workspace menu |
| Workspace — Final Render | `Ctrl+5` | เลย์เอาต์ Final Render | Workspace menu; ไม่ได้เริ่ม render |
| Workspace — All Panels | `Ctrl+6` | แสดงทุก panel ตาม workspace นี้ | Workspace menu |
| Workspace — Full Screen | `Ctrl+7` | เข้า/ออกเต็มหน้าจอ | Workspace menu |
| Workspace — Motion Director | `Ctrl+8` | แสดง panel ที่เกี่ยวกับ Motion Director | Workspace menu |
| Toolbar — Project | `Ctrl+Shift+1` | แสดง/ซ่อน Project Bar | toolbar/menu ของ workspace |
| Toolbar — General | `Ctrl+Shift+2` | แสดง/ซ่อน General Bar | toolbar/menu ของ workspace |
| Toolbar — Camera | `Ctrl+Shift+3` | แสดง/ซ่อน Camera Bar | toolbar/menu ของ workspace |
| Toolbar — Physics | `Ctrl+Shift+4` | แสดง/ซ่อน Physics Bar | toolbar/menu ของ workspace |
| Toolbar — Modify Tools | `Ctrl+Shift+5` | แสดง/ซ่อน Modify Tools | toolbar/menu ของ workspace |
| Toolbar — Motion Director | `Ctrl+Shift+6` | แสดง/ซ่อน Motion Director Bar | toolbar/menu ของ workspace |
| Toolbar — Global Illumination | `Ctrl+Shift+7` | แสดง/ซ่อน Global Illumination Bar | toolbar/menu ของ workspace |
| Toolbar — Menu Bar | `Ctrl+F11` | แสดง/ซ่อน Menu Bar | ใช้เมื่อแถบเมนูถูกซ่อน |
| Focus — Timeline | `Shift+F3` | ย้ายโฟกัสไป Timeline | คลิกพื้นที่ Timeline |
| Focus — Content Manager | `Shift+F4` | ย้ายโฟกัสไป Content Manager | คลิก Content Manager |
| Focus — Scene Manager | `Shift+F5` | ย้ายโฟกัสไป Scene Manager | คลิก Scene Manager |
| Focus — Modify | `Shift+F6` | ย้ายโฟกัสไป Modify panel | คลิก Modify panel |
| Focus — Visual Panel | `Shift+F7` | ย้ายโฟกัสไป Visual panel | คลิก Visual panel |
| Focus — Mini Viewport | `Shift+F8` | ย้ายโฟกัสไป Mini Viewport | คลิก Mini Viewport |
| Focus — Animation Layer | `Shift+F11` | ย้ายโฟกัสไป Animation Layer | คลิก Animation Layer panel |
| Focus — Curve Editor | `Shift+F12` | ย้ายโฟกัสไป Curve Editor | คลิก Curve Editor |
| Panels — Online Manual | `F1` | เปิดคู่มือออนไลน์ | Help > Online Manual |
| Panels — Timeline | `F3` | แสดง/ซ่อน Timeline | Window > Timeline หรือปุ่ม Show Timeline บน Play Bar |
| Panels — Content Manager | `F4` | แสดง/ซ่อน Content Manager | Window menu/ปุ่ม panel |
| Panels — Scene Manager | `F5` | แสดง/ซ่อน Scene Manager | Window menu/ปุ่ม panel |
| Panels — Modify | `F6` | แสดง/ซ่อน Modify panel | Window menu/ปุ่ม panel |
| Panels — Visual Settings | `F7` | แสดง/ซ่อน Visual panel | Window menu/ปุ่ม panel |
| Panels — Mini Viewport | `F8` | แสดง/ซ่อน Mini Viewport | Window menu/ปุ่ม panel |
| Panels — Play Bar | `F9` | แสดง/ซ่อน Play Bar | Window menu/ปุ่ม panel |
| Panels — Animation Layer | `F11` | แสดง/ซ่อน Animation Layer panel | Window menu/ปุ่ม panel |
| Panels — Curve Editor | `F12` | แสดง/ซ่อน Curve Editor panel | Window menu/ปุ่ม panel |
| Panels — Packager | `Ctrl+F4` | แสดง/ซ่อน Packager | Window menu/ปุ่ม panel |
| Panels — MD Controls | `Ctrl+F5` | แสดง/ซ่อน Motion Director Controls | Window menu/ปุ่ม panel |
| Panels — MD Behavior Manager | `Ctrl+F6` | แสดง/ซ่อน MD Behavior Manager | Window menu/ปุ่ม panel |
| Panels — MD Triggers | `Ctrl+F7` | แสดง/ซ่อน MD Triggers | Window menu/ปุ่ม panel |
| Panels — Preference | `Ctrl+P` | แสดง/ซ่อน Preference | Edit > Preference |
| Panels — Project Settings | `Ctrl+Shift+P` | แสดง/ซ่อน Project Settings | Project > Project Settings |
| Panels — Hotkey Manager | ``Ctrl+` `` | แสดง/ซ่อน Hotkey Manager | Edit > Hotkey Manager; ปรับ/คืนค่าเริ่มต้นได้ |
| On-Screen — Transform Gizmo | `Ctrl+Q` | แสดง/ซ่อน transform gizmo | viewport; ใช้ปุ่ม gizmo บน toolbar ได้ |
| On-Screen — Grid | `Ctrl+G` | แสดง/ซ่อนพื้นกริด 3D | viewport; View > Grid |
| On-Screen — Display Info | `Ctrl+F` | แสดง/ซ่อนข้อมูล FPS | viewport; View > Display Info |
| On-Screen — World Axis | `Ctrl+A` | แสดง/ซ่อนแกนโลก | viewport; View > World Axis |
| On-Screen — Dummy Props | `Ctrl+D` | แสดง/ซ่อน Dummy props | viewport; ใช้เมนูแสดงผล |
| On-Screen — TAA | `Shift+T` | เปิด/ปิด Temporal Anti-Aliasing | viewport/display settings |
| On-Screen — Wireframe on Shade | `Alt+2` | แสดง/ซ่อน wireframe ทับบน shaded model | viewport/display settings |
| On-Screen — Wireframe | `Alt+3` | แสดง/ซ่อน wireframe | viewport/display settings |
| On-Screen — Orthogonal | `Shift+H` | สลับ Perspective/Orthogonal | viewport/camera view |
| On-Screen — Current Frame Preview | `F10` | เปิด current-frame render preview | กดปุ่ม Image ในหน้าต่าง preview; ไม่ใช่ full video render |
| Working Area — Select | `Q` | เปิด Select tool | viewport/working area; คลิกไอคอน Select |
| Working Area — Select All | `Shift+A` | เลือกวัตถุทั้งหมดในฉาก | Scene Manager/viewport |
| Working Area — Move | `W` | เปิด Move tool | viewport; คลิกไอคอน Move |
| Working Area — Rotate | `E` | เปิด Rotate tool | viewport; คลิกไอคอน Rotate |
| Working Area — Scale | `R` | เปิด Scale tool | viewport; คลิกไอคอน Scale |
| Move tool (gizmo hidden) | ล้อเมาส์ซ้าย / right mouse / both buttons | ย้าย X-Y / ย้าย Z / หมุน Z | viewport; ใช้ gizmo หากต้องการแก้แกนอย่างเห็นภาพ |
| Rotate tool (gizmo hidden) | left mouse / right mouse / both buttons | หมุน Z / หมุน Y / หมุน X | viewport; ใช้ gizmo เพื่อเลือกแกนชัดเจน |
| Scale tool (gizmo hidden) | left mouse / right mouse / both buttons | scale uniform / scale Z / scale X-Y | viewport; ใช้ gizmo เพื่อคุมแกน |
| Working Area — Undo | `Ctrl+Z` | ย้อนการทำงานล่าสุด | Edit > Undo |
| Working Area — Redo | `Ctrl+Y` | ทำซ้ำสิ่งที่ undo | Edit > Redo |
| Working Area — Duplicate | `Ctrl+Shift+D` | ทำสำเนาวัตถุที่เลือก | Edit > Duplicate |
| Working Area — Isolate Selection | `Ctrl+B` | แสดงเฉพาะวัตถุที่เลือกใน viewport | คลิกขวาวัตถุ/viewport > Isolate Selection; ใน Timeline `Ctrl+B` คือ Break |
| Working Area — Visible | `Ctrl+Shift+H` | ซ่อนวัตถุที่เลือกใน viewport | Scene Manager > Visible |
| Working Area — Duplicate Object | `Ctrl`+ลาก Move/Rotate/Scale | ทำสำเนาวัตถุขณะ transform | viewport; ปล่อย Ctrl เพื่อย้ายต้นฉบับตามปกติ |
| Working Area — Delete Object | `Delete` | ลบวัตถุที่เลือก | Edit > Delete; ตรวจ selection ก่อน |
| Working Area — Selection | `Ctrl`+คลิกซ้าย | เลือกหลายวัตถุ | Scene Manager/viewport |
| Generate Textured Object | ลาก texture มาพื้นที่ว่างด้วยปุ่มขวา | เปิดเมนูสร้างวัตถุจาก texture | Content Manager ไป viewport; เลือกตัวเลือกในเมนู |
| Assign Texture Channel | ลาก texture ไป object ด้วยปุ่มขวา | เลือก object/channel ปลายทางของ texture | เลือกปลายทางจากเมนูที่เปิดขึ้น |
| Create Objects | คลิกขวาบนพื้นที่ว่าง | เปิดเมนูสร้าง light/path/camera หรือเอา animation ออก | viewport; ตรวจตัวเลือกก่อนคลิก เพราะมีคำสั่งลบ animation ทั้งโปรเจกต์ |
| Playback — Play/Pause | `Space` | เล่น/หยุดโปรเจกต์ | Play Bar. ใน Puppet panels Space เริ่ม preview ได้ด้วย จึงตรวจโหมดก่อน |
| Playback — Previous/Next Frame | `←` / `→` | ไปเฟรมก่อน/ถัดไป | Play Bar หรือ Timeline |
| Playback — Start/End | `,` / `.` | ไปต้น/ท้ายโปรเจกต์ | Play Bar หรือ Timeline |
| Align To | `Ctrl+L` | จัดวัตถุที่เลือกให้สัมพันธ์กับอีกวัตถุ | Modify > Align; เลือกเป้าหมาย |
| Material — Pick Material | `B` | เลือก material จากพื้นผิว object | Material panel > Pick Material แล้วคลิกผิว |
| Light — Light/Object Switch | กดค้าง `/` | ชั่วคราวสลับเป็น Light Rotation mode | viewport; ทำงานในบริบทไฟ/วัตถุ |
| Light — Rotate IBL | `Shift+I` | เปิด/ปิดเครื่องมือหมุน IBL | Visual/IBL controls |
| Snap — Angle Snap | `Ctrl+E` | เปิด/ปิด snap มุมตอนหมุน | Preference > Control |
| Snap — Grid | `Ctrl+W` | เปิด/ปิด snap เข้ากริดตอนย้าย | Preference > Control |
| Snap — Model | `Ctrl+M` | เปิด/ปิด snap เข้าผิววัตถุอื่น | Preference > Control |
| Camera View — Pan | `X` | เข้าโหมด pan กล้อง | viewport ต้องรับโฟกัส; คลิก Pan tool |
| Camera View — Zoom | `Z` หรือ wheel | เข้า Zoom tool/ซูมด้วยล้อเมาส์ | viewport; กด mouse buttons ทั้งสองเพื่อเร่ง zoom ตามคู่มือ |
| Camera View — Orbit | `C` | เข้าโหมด orbit | viewport; คลิก Orbit tool |
| Camera View — Roll | `V` | เข้าโหมด roll | viewport; คลิก Roll tool |
| Camera in Object Editing — Move | `Alt`+ปุ่มซ้าย | เคลื่อนกล้อง | viewport; camera/object editing mode |
| Camera in Object Editing — Rotate | `Alt`+ปุ่มขวา | หมุนกล้อง | viewport; camera/object editing mode |
| Camera in Object Editing — Zoom | `Alt`+ปุ่มซ้าย+ขวา | ซูมกล้อง | viewport; camera/object editing mode |
| Camera — Speed | กด `Shift` ระหว่าง zoom/pan/roll/orbit | เพิ่มความเร็วการเคลื่อน 10 เท่า | ปล่อย Shift เพื่อกลับความเร็วปกติ |
| Camera — Home | `Home` | จัดกล้องเป็นมุม 45° มองวัตถุที่เลือก | viewport; ต้องเลือกวัตถุ |
| Quick Camera Positioning | `A` ซ้าย, `S` ขวา, `D` หลัง, `F` หน้า, `G` บน, `J` ใบหน้า, `K` ทั้งหมด | จัดมุมมองเร็วรอบ object ที่เลือก | viewport/Quick Camera Positioning; `F` ที่นี่หมายถึงมองด้านหน้า ไม่ใช่ Motion Director Free Camera |
| Camera Switch — Previous/Next | `[` / `]` | เปลี่ยนกล้องก่อนหน้า/ถัดไปในรายการ | กล้อง/viewport context; เลือกจาก camera list ได้ |
| Camera Switch — Preview/Custom | `H` | สลับ Preview กับกล้องก่อนหน้า | camera context; อย่าสับสนกับ H ในหน้าจอ/โหมดอื่น |
| Camera Switch — Preview/Switch | `\` | คู่มือจัดคีย์นี้ไว้ในหัวข้อสลับกล้อง แต่คำอธิบายแถวเดียวกันกล่าวถึงการหมุน spotlight จึงยังคลุมเครือ | อย่าใช้เป็นคำสั่งแน่นอนจนกว่าจะตรวจ mapping/คำอธิบายใน Hotkey Manager ของรุ่นที่ติดตั้ง |
| Camera & Object Switch | `U` | สลับระหว่างกล้องปัจจุบันกับวัตถุก่อนหน้า | viewport/camera context |
| Object Transform — Move X | `Alt+←` / `Alt+→` | ย้ายวัตถุตามแกน X | วัตถุเลือกอยู่; viewport/transform context |
| Object Transform — Move Y | `Alt+↑` / `Alt+↓` | ย้ายวัตถุตามแกน Y | วัตถุเลือกอยู่; viewport/transform context |
| Object Transform — Move Z | `Ctrl+↑` / `Ctrl+↓` | ย้ายวัตถุตามแกน Z | วัตถุเลือกอยู่; viewport/transform context |
| Object Transform — Rotate Z | `Ctrl+←` / `Ctrl+→` | หมุนวัตถุตามแกน Z | วัตถุเลือกอยู่; ใน Timeline Ctrl+ลูกศรเปลี่ยนเป็น previous/next key |
| Object Transform — Speed | กด `Shift` ระหว่าง move/scale/rotate | เพิ่มความเร็ว 10 เท่า | ปล่อย Shift เพื่อกลับความเร็วปกติ |

## Shortcuts in Panels — คำสั่งเฉพาะ editor/panel

| Panel / คำสั่ง | คีย์ | ใช้ทำอะไร / ใช้เมื่อไร | บริบทและคลิกแทน |
|---|---|---|---|
| Modify Attribute — Attach Section | `I` | เลื่อนไป Attach section | Modify panel ต้อง active; คลิกหัวข้อ Attach |
| Modify Attribute — Look At Section | `O` | เลื่อนไป Look At section | Modify panel; คลิกหัวข้อ Look At |
| Modify Attribute — Path Section | `P` | เลื่อนไป Path section | Modify panel; คลิกหัวข้อ Path |
| Modify Attribute — UV Settings | `Ctrl+U` | เลื่อนไป UV Settings | Modify panel; คลิกหัวข้อ UV Settings |
| Modify Attribute — Transform | `T` | เลื่อนไป Transform section | Modify panel; คลิกหัวข้อ Transform |
| Modify Attribute — Texture Settings | `Y` | เลื่อนไป Texture section | Modify/Material panel; คลิกหัวข้อ Texture |
| Modify Attribute — Substance | `M` | เลื่อนไป Substance section | Modify/Material panel; คลิกหัวข้อ Substance |
| Modify Attribute — Tessellation | `Ctrl+T` | เลื่อนไป Tessellation | Modify/Material panel; คลิกหัวข้อ Tessellation |
| Modify Attribute — Top | `L` | เลื่อนไปส่วนบนสุด | Modify panel; เลื่อน panel ขึ้น |
| Modify Attribute — Previous/Next Section | `Ctrl+PageUp` / `Ctrl+PageDown` | เลื่อนไป section ก่อน/ถัดไป | Modify panel; คลิกหัวข้อหรือเลื่อน |
| Modify Attribute — Bottom | `Ctrl+End` | เลื่อนไปส่วนล่างสุด | Modify panel; เลื่อนลงสุด |
| Modify Attribute — Expand/Collapse All | `Ctrl++` / `Ctrl+-` | ขยาย/ยุบทุก section | ปุ่มลูกศรขยาย/ยุบใน Modify panel |
| Animation Tab — Motion Puppet | `1` | เปิด Motion Puppet | Animation tab > Motion Puppet |
| Animation Tab — Direct Puppet | `2` | เปิด Direct Puppet | Animation tab > Direct Puppet |
| Animation Tab — Motion/Animation Layer | `N` หรือ `3` | เปิด Motion Layer | Animation tab > Edit Motion/Animation Layer |
| Animation Tab — Reach Target | `4` | เปิด Reach Target | Animation tab > Reach Target |
| Animation Tab — Create Script | `5` | เปิด Create Script | Animation tab > Create Script; ตรวจ panel active ก่อนใช้เลข |
| Animation Tab — Face Puppet | `6` | เปิด Face Puppet | Animation tab > Face Puppet |
| Animation Tab — Face Key | `7` | เปิด Face Layer Key | Animation tab > Face Key |
| Material Tab — Export Preset | `Alt+Shift+P` | ส่งออก preset ของ material ที่เลือก | Material tab > Export Preset |
| Material Tab — External Material | `Alt+Shift+E` | นำเข้าและใช้ไฟล์ material ที่บันทึกไว้ | Material tab > External Material |
| Material Tab — Pick Material | `B` | เลือก material โดยกดคีย์แล้วคลิกผิววัตถุ | Material tab > Pick Material |
| Material Tab — Texture/Substance/UV | `Y` / `M` / `Ctrl+U` | เลื่อนไป section ที่ตรงกัน | Material panel; คลิกชื่อ section |
| Material Tab — Assign Material | `Shift+B` | ใช้ material ที่ pick กับพื้นผิวที่คลิก | Material tab > Assign Material |
| Material Tab — Tessellation | `Ctrl+T` | เลื่อนไป Tessellation section | Material panel; คลิกชื่อ section |
| Content Manager — Change View | `Ctrl+1` | สลับ Small Thumbnail / Large Thumbnail / Details | ปุ่ม View Mode ของ Content Manager |
| Content/Scene Manager — Rename | `F2` | เปลี่ยนชื่อ object | คลิกเลือกชื่อ object แล้ว Rename |
| Content Manager — Multi-select | `Ctrl`+คลิกเลือก | เลือกหลายรายการ | กด Ctrl ค้างและคลิกแต่ละรายการ |
| Content Manager — Previous Folder | `Backspace` | กลับโฟลเดอร์ก่อนหน้า | ปุ่ม Back ของ Content Manager |
| Content Manager — Scroll Top/End | `Home` / `End` | ไปต้น/ท้ายรายการ | scrollbar หรือเลื่อนรายการ |
| Render — Current Frame Preview | `F10` | render ภาพเฟรมปัจจุบันเพื่อ preview | Render panel > Image; ไม่ใช่ render ทั้งโปรเจกต์ |
| Preference Control — Angle/Grid/Model Snap | `Ctrl+E` / `Ctrl+W` / `Ctrl+M` | เปิด/ปิด snap มุม/กริด/โมเดล | Preference > Control |
| Preference Control — Transform Gizmo | `Ctrl+Q` | แสดง/ซ่อน gizmo | Preference > Control หรือ toolbar |
| Preference Grid — Grid | `Ctrl+G` | แสดง/ซ่อนพื้นกริด | Preference > Grid |
| Preference Display — Display Info | `Ctrl+F` | แสดง/ซ่อนข้อมูล viewport | Preference > Display |
| Preference Display — World Axis | `Ctrl+A` | แสดง/ซ่อนแกนโลก | Preference > Display |
| Preference Display — Safe Frame | `Shift+G` | แสดง safe frame สำหรับ final render | Preference > Display หรือ viewport menu |
| Preference Timeline — Audio Scrubbing | `Ctrl+H` | เปิด/ปิดเสียงขณะ scrub Timeline | Preference > Timeline |
| Scene Manager — Create Sub-collection | `C` | สร้าง collection ย่อยว่าง | คลิกขวาใน Scene Manager > Create Collection |
| Scene Manager — Add to New Collection | `N` | ย้าย selection ไป collection ใหม่ | คลิกขวารายการ > Add to New Collection |
| Scene Manager — Bring to Front | `B` | นำ object ออกจาก collection | Scene Manager context menu |
| Scene Manager — Select Hierarchy | `I` | เลือก collection และวัตถุย่อยทั้งหมด | คลิกขวา collection > Select Hierarchy |
| Scene Manager — Select All | `Shift+A` | เลือกทุก object ใน Scene Manager | Edit > Select All หรือคลิก Scene Manager แล้วกด |
| Scene Manager — Wireframe | `Alt+3` | แสดง wireframe | viewport/display mode |
| Scene Manager — Wireframe on Shade | `Alt+2` | ซ้อน wireframe บน shaded object | viewport/display mode |
| Scene Manager — Duplicate | `Ctrl+Shift+D` | ทำสำเนาวัตถุที่เลือก | Edit > Duplicate |
| Motion Director — Start/Stop | `Ctrl+R` | เริ่ม/หยุดเล่น Motion Director | Motion Director controls |
| Motion Director — Reset Camera | `Backspace` | คืนกล้องค่าเริ่มต้น | Motion Director controls |
| Motion Director — Camera View | `F` Free, `G` Full Shot, `H` Close Up, `J` Bird's Eye | เปลี่ยนมุมกล้องระหว่างเล่น | Motion Director hotkey panel; `F` ที่นี่คือ Free Camera |
| Motion Director — Move Character | `W` หน้า, `S` หลัง, `A` ซ้าย, `D` ขวา | ควบคุมการเคลื่อนที่ตัวละคร | Motion Director mode เท่านั้น |
| Motion Director — Speed | กด `Shift` เร็วขึ้น / `Ctrl` ช้าลง | ปรับความเร็วเคลื่อนตัวละคร | Motion Director mode เท่านั้น |
| Motion Director — Data Switch | `[` ก่อนหน้า / `]` ถัดไป | เปลี่ยน data ก่อนหน้า/ถัดไป | Motion Director mode |
| Motion Director — Mode Switch | `F1` ถึง `F12` | เปลี่ยนโหมดตาม hotkey mapping | Motion Director mode; `F1` ที่นี่อาจไม่ใช่ Online Manual |
| Motion Director — Perform | `1` ถึง `0` | เรียก perform action | Motion Director mode เท่านั้น |
| Motion Director Hotkey Panel — Change View | `Ctrl+1` | เปลี่ยน view mode ของ hotkey panel ขณะเล่น | Motion Director hotkey panel |
| Puppet Panels — Preview | `Space` | เริ่ม previewing | Motion/Direct/Face/Prop Puppet panel active |
| Puppet Panels — Record | `Ctrl+Enter` | เริ่ม puppeteering และบันทึก | Puppet panel; ตรวจว่าเลือกตัวละครและโหมดถูกต้อง |
| Face Puppet — Detail | `Ctrl+F2` | เปิด Face Puppet Detail | Face Puppet panel |
| Face Puppet — Profile | `1`, `2`, `3`… | เปลี่ยน profile ระหว่าง preview/record | Face Puppet panel active |
| Face Puppet — Control Template | `Q`, `W`, `E`, `R`, `T`, `Y` | เปลี่ยน Full Face Control template | Face Puppet preview/recording เท่านั้น; ไม่ใช่ viewport tool |

## Timeline Shortcuts — keys และ clips

| กลุ่ม / คำสั่ง | คีย์ | ใช้ทำอะไร / ใช้เมื่อไร | บริบทและคลิกแทน |
|---|---|---|---|
| Common — Previous/Next Frame | `←` / `→` | ไปเฟรมก่อน/ถัดไป | Timeline ต้องรับโฟกัส; ปุ่ม step บน Timeline |
| Common — Previous/Next Key | `Ctrl+←` / `Ctrl+→` | ไป key ก่อน/ถัดไป | Timeline; ใน Viseme ใช้กระโดด key เช่นกัน |
| Common — Zoom In/Out | `+` / `-` | ซูม Timeline | Timeline toolbar; `Alt`+wheel ก็ซูมได้ |
| Common — Fit to Window | `Ctrl+*` | จัดให้เห็นทุกเฟรมของโปรเจกต์ | ปุ่ม Fit to Window; `*` อาจอยู่ numpad |
| Common — Actual Size | `Ctrl+/` | กลับมุมมอง Timeline ขนาดเริ่มต้น | ปุ่ม Actual Size |
| Common — Delete | `Delete` | ลบ key/clip ที่เลือก | Timeline selection; คลิกขวา > Delete |
| Common — Home/End | `Home` / `End` | ไปต้น/ท้าย Timeline | playhead controls |
| Common — Select Keys Continuously | `Shift`+ลากปุ่มซ้าย | เลือก keys ต่อเนื่อง | ลาก selection box บนแถว keys |
| Common — Select Clips Continuously | `Shift`+คลิกปุ่มซ้าย | เลือก clips ต่อเนื่อง | คลิกแต่ละ clip โดยกด Shift |
| Common — Pan View | `Ctrl`+ล้อเมาส์ | เลื่อนมุมมอง Timeline ซ้าย/ขวา | scrollbar แนวนอน |
| Common — Zoom View | `Alt`+ล้อเมาส์ | ซูมเข้า/ออก Timeline | Zoom controls |
| Edit — Add Key | `A` | เพิ่ม key ณ playhead | Add Key button; ใช้ได้เฉพาะ Transform, Motion Layer, Facial Layer, Visible, HDR, IBL, Effect และแทร็กกล้อง/ไฟบางชนิด (Constraint ยกเว้น) |
| Edit — Break | `Ctrl+B` | แบ่ง clip ที่เลือก ณ เวลาปัจจุบัน | Timeline ต้อง active, clip เลือกอยู่; คลิก Break. เป็น Break ปกติที่เก็บข้อมูลเดิมไว้ซ่อนเพื่อขยายกลับได้; อย่าสับสน Isolate Selection ใน viewport |
| Edit — Playback Range On/Off | `'` / `;` | เปิด/ปิด playback range flags สีเหลือง | ปุ่ม range flags บน Timeline toolbar |
| Edit — Sound Settings | `8` | เปิด Sound Settings ของ sound clip ที่เลือก | เลือก sound clip ก่อน; คลิกปุ่ม Sound Settings |
| Edit — Loop Clip | `1` | เปิด Loop mode เพื่อยืด clip แบบวนซ้ำ | เลือก clip แล้วคลิก Loop |
| Edit — Speed Clip | `2` | เปิด Speed mode เพื่อเปลี่ยนความเร็วเมื่อยืดคลิป | เลือก clip แล้วคลิก Speed |
| Edit — Resize Clip | `3` | เปิด Resize เพื่อปรับความยาวคลิป | เลือก clip แล้วคลิก Resize |
| Edit — Motion Direction Control | `4` | เข้าโหมดเปลี่ยนทิศ motion clip | เลือก clip แล้วคลิก Motion Direction Control |
| Edit — Motion Modifier | `5` | เปิด Motion Modifier | เลือก motion clip แล้วคลิก Motion Modifier |
| Edit — Copy/Cut/Paste | `Ctrl+C` / `Ctrl+X` / `Ctrl+V` | คัดลอก/ตัด/วาง keys หรือ clips | เลือกข้อมูลก่อน; Editing Tools/context menu |
| Edit — Duplicate | `Ctrl`+ลากปุ่มซ้าย | ทำสำเนา keys/clips | ลาก selection ด้วย Ctrl ค้าง |
| Viseme — Lips Editor | `7` | เปิด Lips Editor | เลือกตัวละคร/Viseme context; คลิก Lips Editor |
| Viseme — Talking Style Editor | `6` | เปิด Talking Style Editor | คลิก Talking Style Editor |
| Viseme — Next/Previous Key | `Ctrl+→` / `Ctrl+←` | ไป Viseme key ถัดไป/ก่อนหน้า | Timeline/Viseme track active |
| Show Tracks — Object Related | `O` | แสดง tracks ที่เกี่ยวกับ object ที่เลือก | เลือก object แล้วปุ่ม Object Related Tracks |
| Show Tracks — Collect Clip | `Q` | แสดง/ซ่อน Collect Clip track | Track menu > Collect Clip |
| Show Tracks — Transform | `T` | แสดง/ซ่อน Transform track | Track menu > Transform |
| Show Tracks — Motion | `M` | แสดง/ซ่อน Motion track | Track menu > Motion |
| Show Tracks — Reach | `R` | แสดง/ซ่อน Reach track (คู่มือแสดงคำอธิบาย Viseme track) | Track menu; ตรวจชื่อแทร็กในรุ่นที่ใช้ |
| Show Tracks — Viseme | `Z` | แสดง/ซ่อน Viseme track | Track menu > Viseme |
| Show Tracks — Expression | `E` | แสดง/ซ่อน Expression track | Track menu > Expression |
| Show Tracks — Link | `L` | แสดง/ซ่อน Link track | Track menu > Link |
| Show Tracks — Visible | `V` | แสดง/ซ่อน Visible track | Track menu > Visible |
| Show Tracks — Material | `S` | แสดง/ซ่อน Material track | Track menu > Material |
| Show Tracks — Sound | `D` | แสดง/ซ่อน Sound track | Track menu > Sound; ตรวจว่าเลือก Project Sound ตามต้องการ |
| Show Tracks — Spring | `I` | แสดง/ซ่อน Spring track | Track menu > Spring |

## Curve Editor — คีย์ลัดใน Outliner และ Graph View

หน้าทางการนี้อยู่ในหมวด Curve Editor แม้หัวหน้าหน้าจะใช้ชื่อ “Timeline Shortcuts”. ใช้เมื่อ Curve Editor รับโฟกัส; ใน Graph View ต้องให้พื้นที่กราฟ active ส่วน Up/Down อยู่ใน Outliner. `F` ที่นี่จัดกราฟให้เห็น curves ทั้งหมดที่แสดงอยู่ ไม่ใช่ Front Camera ใน viewport หรือ Free Camera ใน Motion Director

| กลุ่ม / คำสั่ง | คีย์ | ใช้ทำอะไร / ใช้เมื่อไร | บริบทและคลิกแทน |
|---|---|---|---|
| Overall — Move Key tool | `M` | สลับเครื่องมือเลือก/ย้าย key | Curve Editor; คลิก Move Key tool |
| Overall — Frame Curves | `F` | จัดมุมมองให้เห็น curves ทั้งหมดที่แสดง | Curve Editor/Graph View; คลิก Frame/Fit Curves |
| Overall — Delete Keys | `Delete` | ลบ keys ที่เลือก | Curve Editor; เลือก key ก่อน แล้วใช้ Delete/context menu |
| Overall — Tree/List View | `V` | สลับ Tree View กับ List View | Curve Editor; ใช้ปุ่มมุมมองของ panel |
| Overall/Graph — Interpolation Auto | `Ctrl+1` | ตั้ง interpolation เป็น Auto | เลือก key(s) ใน Graph View; คลิก interpolation menu |
| Overall/Graph — Interpolation Smooth | `Ctrl+2` | ตั้ง interpolation เป็น Smooth | เลือก key(s) ใน Graph View |
| Overall/Graph — Interpolation Spline | `Ctrl+3` | ตั้ง interpolation เป็น Spline | เลือก key(s) ใน Graph View |
| Overall/Graph — Interpolation Linear | `Ctrl+4` | ตั้ง interpolation เป็น Linear | เลือก key(s) ใน Graph View |
| Overall/Graph — Interpolation Step | `Ctrl+5` | ตั้ง interpolation เป็น Step | เลือก key(s) ใน Graph View |
| Overall/Graph — Interpolation Fast | `Ctrl+6` | ตั้ง interpolation เป็น Fast | เลือก key(s) ใน Graph View |
| Overall/Graph — Interpolation Slow | `Ctrl+7` | ตั้ง interpolation เป็น Slow | เลือก key(s) ใน Graph View |
| Overall/Graph — Edit Motion Layer FK | `N` | เปิด Edit Motion Layer panel ที่แท็บ FK | Curve Editor; คลิก Animation > Edit Motion Layer แล้วเลือก FK |
| Overall/Graph — Break Handle Reciprocity | `B` | แยกความสัมพันธ์ของ key handles | เลือก key ใน Graph View; ใช้ปุ่ม handle บนแถบกราฟ |
| Overall/Graph — Unify Handles | `U` | รวม key handles และคืน reciprocity | เลือก key ใน Graph View; ใช้ปุ่ม handle บนแถบกราฟ |
| Overall/Graph — Previous/Next Frame | `←` / `→` | ไปเฟรมก่อนหน้า/ถัดไป | Curve Editor; ใช้ playback controls |
| Outliner — Previous/Next Component | `↑` / `↓` | ย้าย focus ไป component ก่อนหน้า/ถัดไป | Curve Editor Outliner; คลิกรายการ component |
| Graph — Move Keys Horizontally/Vertically | กด `Shift` ค้างแล้วลากด้วยปุ่มซ้าย | ย้าย keys แนวนอนหรือแนวตั้งตามทิศทางลาก | Graph View ต้อง active และ key ถูกเลือก; ลาก key โดยตรง |
| Graph — Add Keyframe | `A` | เพิ่ม keyframe ให้ทุก curve ที่กำลังแสดง | Graph View; คลิก Add Key ใน panel |
| Graph — Delete Keys | `Delete` | ลบ keys ที่เลือก | Graph View; เลือก keys ก่อน |
| Graph — Frame Curves | `F` | จัดกราฟให้เห็น curves ทั้งหมดที่แสดง | Graph View; คลิก Frame/Fit |
| Graph — Zoom | ล้อเมาส์ | ซูมเข้า/ออก | pointer อยู่เหนือ Graph View |
| Graph — Horizontal Zoom | `Ctrl`+ล้อเมาส์ | ซูมแกนนอน | pointer อยู่เหนือ Graph View |
| Graph — Vertical Zoom | `Shift`+ล้อเมาส์ | ซูมแกนตั้ง | pointer อยู่เหนือ Graph View |

## ตัวอย่างที่คีย์บอร์ดเร็วกว่า และงานที่ควรคลิก

- ไป Timeline: `F3` เปิดแผง แล้ว `Shift+F3` ให้โฟกัส; กด `Home`/`End` หรือ `Ctrl+←`/`Ctrl+→` เพื่อทบทวนเฟรม/key
- ตรวจทั้งความยาวโปรเจกต์: `Ctrl+*` Fit to Window; ถ้าปุ่ม `*` ใช้ไม่ได้ ให้คลิก Fit to Window และตรวจปลายแทร็กด้วยตา
- แสดงเสียง/Viseme/Expression: คลิก Timeline แล้วกด `D`/`Z`/`E`; ใช้ Track menu เมื่อไม่แน่ใจว่าคีย์ส่งไปแผงไหน
- แบ่ง/คัดลอกคลิป: เลือกคลิปและวาง playhead ก่อนใช้ `Ctrl+B`/`Ctrl+C`; ใช้ปุ่ม Break/Editing Tools หากไม่มั่นใจว่า Timeline รับโฟกัส
- เปิด import ด้วย `Ctrl+I` ได้ แต่เลือกไฟล์และชนิด Sound ใน dialog ด้วยการคลิก/ตรวจสถานะเอง; shortcut ไม่รับประกันว่าเสียงเข้า Project Sound track
- การเลือก pose, กล้อง Switcher, ตั้งชื่อ/path, ตั้งค่าตัวเลข, แก้ Look At, แสง และ framing เห็นผลได้ชัดกว่าด้วย UI; คีย์ลัดไม่ทดแทนการตรวจภาพ/เล่นจริง
- `F` เป็นตัวอย่างชัดเจนของ context-sensitive key: Quick Camera Positioning = Front, Motion Director = Free Camera; ใน editor อาจไม่ทำอย่างใดอย่างหนึ่งนี้

## Hotkey Manager และข้อจำกัดเวอร์ชัน

เปิด Hotkey Manager ด้วย ``Ctrl+` `` หรือเมนู Edit > Hotkey Manager; คู่มือระบุว่าสามารถเปลี่ยน hotkey ได้ และหน้า Manager มีคำสั่ง Restore to Default. ตรวจ mapping ที่ติดตั้งจริงก่อนใช้คีย์ที่จำเป็น เพราะผู้ใช้สามารถตั้งค่าใหม่ได้

ตารางหลักเป็นค่าจากคู่มือออนไลน์รุ่น 8.0. หน้าเปิด Timeline รุ่น 8.7 ยืนยันว่าใช้ `F3`, ปุ่ม Show Timeline บน Play Bar หรือ Window > Timeline ได้ แต่ไม่ได้ยืนยัน shortcut อื่นทั้งหมดใน 8.7. ยังไม่ได้เปิด iClone บนเครื่องเพื่ออ่านรุ่น/ทดสอบคีย์จริง; เมื่อคำสั่งในแอปไม่ตรง ให้ถือ Hotkey Manager และเมนูที่แสดงอยู่เป็นข้อมูลล่าสุด

## แหล่งอ้างอิงทางการของ Reallusion

- [iClone 8.0 — Global Shortcuts](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/90_Keyboard_Shortcuts/Global_Shortcuts.htm)
- [iClone 8.0 — Shortcuts in Panels](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/90_Keyboard_Shortcuts/Editor_Mode_Shortcuts.htm)
- [iClone 8.0 — Timeline Shortcuts](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/90_Keyboard_Shortcuts/Timeline_Shortcuts.htm)
- [iClone 8.0 — Curve Editor Keyboard Shortcuts](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/58-Curve-Editor/Keyboard_Shortcuts.htm)
- [iClone 8.0 — Hotkey Manager](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/03-Introducing-the-User-Interface/Hotkey-Manager.htm)
- [iClone 8.7 — Launching Timeline](https://manual.reallusion.com/iclone-8/Content/ENU/8.7/51-Animation-Timeline-Editing/Launching-Timeline.htm)
- [iClone 8.0 — Timeline Operation: Basic](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/51-Animation-Timeline-Editing/Timeline-Operation-Basic.htm)
- [iClone 8.0 — Setting Project Start/End Frame Markers](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/51-Animation-Timeline-Editing/Setting_Mark_In_and_Mark_Out.htm)
