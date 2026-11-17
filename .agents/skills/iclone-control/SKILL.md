---
name: iclone-control
description: How to drive iClone 8 without the mouse - the job watcher, ic8_gui.ps1 GUI chores, popups, crashes. Use whenever a step needs iClone.
---
# Drive iClone (no mouse, works on any PC)

- Once per iClone launch: Script > Load Python > `scripts/ic8_watch.py`. Jobs: drop a `.py` into `%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\run\` -> renamed `.done`/`.err` + `<name>.log`. Or `ic8_gui.ps1 job <file.py>`.
- Bridge says BLOCKED: a `.py` was pending at start -> empty `run\`, restart iClone.
- GUI chores, one command each: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\ic8_gui.ps1 <shot|save|saveas|open|reopen|switch|tozero|sound|lip|render>`.
  Keys are sent only while iClone is the foreground window; never screen coordinates.
- Start popups: `scripts/ic8_ui.ps1 click "OK"` / `click "No, thank you."`. "Unsaved project data" -> Esc.
- Write job files with heredocs (printf breaks newlines). RLPy: `IsVisible(RTime)` not GetVisible; only point/spot lights have SetRange.
- Do not drive iClone for tool-building or planning unless the user asks; test in test projects.
- More API notes: `docs/iclone-key-SKILL.md`, `docs/rlpy_lessons.md`.
