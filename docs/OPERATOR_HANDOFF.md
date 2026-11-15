# Operator handoff — live source index
This is a durable index, NOT a frozen story status. Refresh live source files at the start of EVERY chat.
Current story and per-part progress: docs/CURRENT_STORY.md (latest dated entries; inspect end of file).
Production rules: AGENTS.md, docs/rules.md, docs/WORKFLOW.md, docs/iclone-key-SKILL.md.
Event-specific workflow when applicable: docs/event_clip_workflow.md.
Historical status only (do NOT treat as current): docs/CURRENT_STATUS.md and data/project_status.json, both contain old ดวงเมียน้อย records.
Determine current story from latest applicable docs/CURRENT_STORY.md and actual current iClone scene; if mismatch, report it.
Before acting: validate tunnel, project root, iClone process, watcher via actual inspect_scene result; marker alone is not heartbeat.
When a new story or part is completed, append dated verified progress to docs/CURRENT_STORY.md and update this index only if paths change.
Do not save/render/edit iClone on bootstrap. Do not infer permission from previous chats.
