# มหาอกหัก, part 2 (audio_output\2.mp3, 81.5 s + 5 s tail = 86.5 s)

Scene: `G:\ไดรฟ์ของฉัน\มหาอกหัก (นิทาน)\ฉาก\ภายในโบสถ์ของวัดอีกวัด.iProject` (floor z 25774).
Villagers sit in a circle around (33, 566); monk sits at (33, 966) facing them (yaw 0). Hide/delete avatar `Sunee`.

## Cast (files under `มหาอกหัก (นิทาน)\มหาอกหัก\`)
| id | file | seat | lip-sync line (s) |
|---|---|---|---|
| monk | 1. พระมหาสมชาติ\พระมหาสมชาติ เจ้าอาวาส วัย 48 | (33,966) | – |
| im | 3. นายอิ่ม มัคนายก\นายอิ่ม มัคนายกวัด วัย 55 | circle 90° | 13.4–24.6 |
| old | 2. ชาวบ้าน\ชาวบ้าน ชายแก่ วัย 68 | circle 162° | 1.4–4.7 |
| woman | 2. ชาวบ้าน\ชาวบ้าน หญิงวัยกลางคน วัย 45 | circle 18° | 31.7–40.5 |
| young | 2. ชาวบ้าน\ชาวบ้าน ชายหนุ่ม วัย 25 | circle 234° | 40.8–50.6 |
| commf | 4. กรรมการวัด + ลูกศิษย์วัด\กรรมการวัด หญิง วัย 52 | circle 306° | – |

## Shots (cut on narration pauses; all with DOF blur in this interior)
| time | narration | picture | lens |
|---|---|---|---|
| 0–7.0 | บวชเป็นเณรตั้งแต่จบ ป.6 ชาวบ้านคนหนึ่งพูด | old villager speaking | 100 |
| 7.0–13.45 | ได้รับนิมนต์มาเป็นเจ้าอาวาสใหม่ๆ | monk chest-up close-up (อกขึ้นไป; do not show lower robe) | 100 |
| 13.45–24.88 | พ่อแม่สิ้น ตายายเลี้ยง นิสัยดี | Im telling | 100 |
| 24.88–31.74 | นายอิ่มเล่าให้ญาติโยมฟัง | OTS over villagers onto Im | 80 |
| 31.74–40.81 | แหม น่าเลื่อมใส… | woman speaking | 100 |
| 40.81–50.80 | ไม่มีเรื่องเสื่อมเสีย… | young man speaking | 100 |
| 50.80–53.82 | ใครอีกคนเล่าเสริม | tight reaction MCU of p2_commf (no legs in frame) | 100 |
| 53.82–75.5 | ปฏิบัติตนงดงาม… | monk chest-up (อกขึ้นไป), gentle push-in without showing lower robe | 100 |
| 75.5–86.5 | มีแต่เสียงชื่นชม ปากต่อปาก | closing chest-up reaction MCU of villager; never show seated legs | 100 |

## Speech/lip-sync QA required before next render (2026-11-07)
User requires every real in-scene speaker to actually articulate the correct words on the correct timeline. The following intervals come from existing pre-cut WAV metadata, **not yet from visual verification**:
- p2_old: 1.4–4.7 s; WAV 3.3 s
- p2_im: 13.4–24.6 s; WAV 11.2 s
- p2_woman: 31.7–40.5 s; WAV 8.8 s
- p2_young: 40.8–50.6 s; WAV 9.8 s
- Re-evaluate speaker attribution and any additional dialogue around 50.8–75.5 s from full transcript/audio, especially p2_commf vs narration.
- For each speaker, verify viseme/lip channel and compare at least two speaking frames to one silent frame. The 3 Look-front face clips on each avatar are NOT proof of lip sync. Check for duplicated audio when WAV is attached to avatar alongside Project Sound. Keep AccuPOSE/body clips unchanged.
- Do not declare this part finished or render again until dialogue sync is demonstrably correct.

## New mandatory audio import/trim workflow (2026-11-07)
User explicitly corrected the workflow. For every speaking character in Part 2, import the FULL C:\Users\Apinan\Downloads\audio_output\2.mp3 to THAT avatar using iClone's Voice/AccuLips tools first; then use iClone Timeline Split/Cut/Trim to REMOVE intervals in which that character does not speak. Repeat with full 2.mp3 for every speaker. Keep full Project Sound unchanged, prevent doubled audible dialogue, do not import externally pre-cut p2_*.wav as the source of lip sync. Those WAVs may only be timing references.
Existing tentative speaker windows: old 1.4-4.7, im 13.4-24.6, woman 31.7-40.5, young 40.8-50.6 seconds. Refine against the original audio/transcript, and audit who speaks in the remaining sections. A successful import must create Viseme/Voice clips, which were still absent (0 Viseme clips across all 6 avatars at last direct inspection).
Must preserve AccuPOSE, confirm real mouth movement at multiple speaking frames and silence elsewhere; NO video render until verified.
