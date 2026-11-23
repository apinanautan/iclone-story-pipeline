---
name: paths
description: Find the motion library, the shared Google Drive story folders, the save/video folders and the Desktop on THIS PC without hardcoding drive letters (G:, E: differ per PC). Use before writing any file path in a spec, script or message.
---
# Paths on any PC (never hardcode G:\ or E:\)

```
python scripts/paths.py                                   # find + print every root on this PC
python scripts/paths.py "{MOTION}\Digital Soul 100+\Sad\01_Sad_Lo.italk"    # expand one path
```
| placeholder | what | on this PC (example) | new PC if missing |
|---|---|---|---|
| `{MOTION}` | motion library (has `motions.csv` + `Digital Soul 100+`) | `{MOTION}` | searched on every drive |
| `{DRIVE}` | Google Drive "ไดรฟ์ของฉัน / My Drive": story audio, scripts, scenes, avatars. **READ ONLY** (except publishing the final video) | `{DRIVE}` | searched on every drive |
| `{SAVE}` | saved .iProject parts | `{SAVE}` | `Documents\iClone Story Save` (created) |
| `{VIDEO}` | rendered videos | `{VIDEO}` | `Videos\iClone Story` (created) |
| `{DESKTOP}` | this user's Desktop (cut audio) | `C:\Users\<user>\Desktop` | same |

- Write placeholders in part specs (`parts/*.json`), story files (`stories/*.json`) and skills: `"motion": "{MOTION}\\04_CC MixMove_Female\\Stand03.iMotion"`. `ic8_part.py` and `cut_audio.py` expand them automatically.
- In your own Python: `sys.path.insert(0, "scripts"); from paths import expand, root; expand(obj)` / `root("MOTION")`.
- Found roots are cached in `paths.local.json` (repo root, not in git). Wrong guess? Edit that file or set env `IC_MOTION`, `IC_DRIVE`, `IC_SAVE`, `IC_VIDEO`, `IC_DESKTOP`.
- If a root cannot be found, ask the user where it is - do not guess a drive letter.
