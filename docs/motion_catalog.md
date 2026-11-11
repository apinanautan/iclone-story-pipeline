# Motion / pose catalog (what each clip actually looks like) — write here every time a motion is used or tested

User (2026-11-10): do NOT reuse the same few motions every part; the library is huge. Pick something new when it fits, and record what it looks like here so the next pick is informed. Verify by a still before trusting a name.

Library roots: `G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น\โมชั่น\` (CC MixMove 03_Male / 04_Female) and `G:\ไดรฟ์ของฉัน\.ไฟล์ต่างๆ (ห้ามลบ)\โมชั่น\` (MixMoves Communication 200, MographMotion *_Sad, Daily Life, Studio Mocap...). Hand poses: `C:\Users\Public\Documents\Reallusion\Reallusion Templates\Animation\Gesture\{Hold,Sign}\*.iHand`.

| Motion | Looks like (verified by stills) | Good for | Avoid when | Used in |
|---|---|---|---|---|
| 04_Female\Stand00 | neutral idle; sometimes a hand rises to the head/hair (seen on Navee, villager, mistress) | calm bystander | close-ups (hand to head intrudes) | p1 kids, p2 |
| 04_Female\Stand01 | idle with a clear raised-hand wave gesture (~80% of clip) | explaining/greeting | any quiet scene | p1 test only |
| 04_Female\Stand02 | hands on hips, body angled; mother-scolding look | angry/confident woman | sad scenes | p1 mother, p2 mother, p3 mother |
| 04_Female\Stand03 | quiet, arms down, very still | background / mistress listening | – | p2 mistress, p3 test |
| 04_Female\Stand04 | quiet, arms down, very still | kids / quiet | – | p2 villager, p3 Navee |
| 03_Male\Stand00 | neutral idle, arms down | any man/boy | – | p1 Niwat, p3 father + Niwat |
| 04_Female\Walk / 03_Male\Walk | Walk.iMotion MOVES the avatar's root (about 65 cm/s at speed 0.6, ~100 cm/s at 1.0) — do not also key position during the walk and do not switch to a Stand clip afterwards (it snaps back) | leaving the scene | – | p3 |
| 03_Male\Walk | normal male gait | father leaving | – | p3 |
| Hand pose Hold\Hold Gently.iHand | LoadFile with the avatar selected at t=0 curls BOTH hands softly (natural); lasts through walking | default for every character (flat straight hands look bad) | when a gesture is needed | p3 (all) |

To try next (not yet verified): MixMoves Communication 200 Female/Male Stand\*_Response (Sad, Hand on Hips, Arms Crossed...), MographMotion 02_Female Stand03/04_L_Sad (sad standing), Endearment Hug 01-12 _F/_M (paired hugs).

Also: Look-at keys turn the head 50-80 deg toward the target; face clip "Look front" does not.

| Walk (F/M) — single stretched clip | Female natural 5.37 s, male 4.68 s at speed 1; root moves ~96 cm/s (F) / ~102 cm/s (M) at speed 1; chained Walk clips snap back at each boundary | slow sad walk home (speed 0.4) or walking away | any chain of walk clips | p3 |


## คลังโมชั่นที่ค้นพบและจะใช้กับท่อน 3 (สำรวจ 2026-11-11)
Root: `G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น` — 4,742 .rlMotion, 1,286 .iMotion, 129 .iMotionPlus, 270 .italk, 8 .iFace

| บีต | คลิปที่จะใช้ (ยังไม่ verified ด้วย still) | เหตุผล |
|---|---|---|
| 3.2 พ่อหัน+เดินออก | `โมชั่น\03_CC MixMove_Male\Walk_Turn.iMotion` (มี _Mirror/F ด้วย) แล้วต่อ `Walk.iMotion` / `Walk ชาย.iMotion` — **ห้ามต่อ walk หลายคลิป (root snap)** ใช้คลิปเดียว stretch | มี transition หัน→เดินในคลิปเดียว ลด snap |
| 3.2 เมียน้อยตาม | `Studio Mocap - Office Work Bundle\...\Movement\Walk_Normal_F.rlMotion` (หรือ Walk F) คนละความเร็ว/สปีด 0.9 | เด็ก/ผู้หญิงเดินช้ากว่า |
| 3.3 แม่เจ็บ/ร้องไห้ | `โมชั่น\MographMotion\02_Female\Stand03_L_Sad.iMotion` หรือ `Scared Mocap Animations\SCR_Crying_Over_Body_Standing_01_Loop` | มี sad/cry loop จริง ไม่ต้องคีย์มือ |
| 3.3 แม่กอดลูก | `Endearment Hug 01-12 _F/_M` (ตาม catalog) + `Studio Mocap-Office Work...\Reception\Greeting_Hug01_M.rlMotion`, `Greeting_HugKiss_F.rlMotion`, `Hold Me _F.iMotionplus` | เลือกท่ากอดที่ไม่ทะลุ; ถ้าทะลุใช้ `Arm on Sholder_M1.rlmotion` (มือจับไหล่) แทน |
| 3.3 แม่คุกเข่าปลอบลูกที่นั่ง | `Kneel02.iMotion` / `03_CC MixMove_Male\Kneel01_to_Kneel02.iMotion` (147 คลิป kneel) | เด็กนั่งอยู่ ศีรษะ z≈183 ต้องลดตัวลง |
| เด็กกลัว/เสียใจ | `Scared Mocap Animations\*` (scared loop) + face `*_Sad` | หลีกเลี่ยงขยับพร้อมกัน ให้เหลื่อม 0.3-0.6s |
| 3.4 เดินกลับบ้าน | `04_CC MixMove_Female\Walk.iMotion` สปีด ~0.4 (ช้าเศร้า) คลิปเดียว stretch | ตาม lesson walk root |
| 3.1 ปรับการแสดงพ่อ | `Studio Mocap - Conversation\*`, `Motion_-_TalkListen\*`, `Digital Soul 100+\*` | มีคลิปพูด/ฟังจริง ถ้าต้องเปลี่ยนจาก idle |

Hug Kid 01_M + Hug Kid 01_K verified for Part 3: iClone Endearment Family and Friends pair, mother adult retarget plus one child, global 59.133–63.667. Must position child at mother hand reach (shift x+90,y+55) and keep second child visibly nearby. Verified both children and red material after texture load. Do not assume both kids have true hand contact.
