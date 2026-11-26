---
name: iclone-control
description: Drive iClone 8's non-save chores with the watcher and helpers. Save projects only by manually clicking the File menu; use whenever a step needs iClone.
---
# Drive iClone (manual menu save; no save automation)

- Once per iClone launch: Script > Load Python > `scripts/ic8_watch.py`. Jobs: drop a `.py` into `%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\run\` -> renamed `.done`/`.err` + `<name>.log`. Or `ic8_gui.ps1 job <file.py>`.
- Bridge says BLOCKED: a `.py` was pending at start -> empty `run\`, restart iClone.
- Use `scripts\ic8_gui.ps1` only for non-save chores (`shot|open|reopen|switch|tozero|sound|lip|render`).
- **Saving rule (user 2026-11-26):** save projects only by clicking the visible iClone `File > Save Project` or `File > Save Project As` menu in the live UI. Never save with a Python/RLPy script, watcher, CLI, PowerShell helper, or simulated keyboard shortcut. The helper's `save` and `saveas` commands are disabled; `scripts/ic8_save.py` has been removed.
- After manually saving, reopen the same `.iProject` from iClone's `File > Open` menu and confirm it fully loads before reporting success or rendering.
- Start popups: `scripts/ic8_ui.ps1 click "OK"` / `click "No, thank you."`. "Unsaved project data" -> Esc.
- Write job files with heredocs (printf breaks newlines). RLPy: `IsVisible(RTime)` not GetVisible; only point/spot lights have SetRange.
- Do not drive iClone for tool-building or planning unless the user asks; test in test projects.
- More API notes: `docs/iclone-key-SKILL.md`, `docs/rlpy_lessons.md`.
