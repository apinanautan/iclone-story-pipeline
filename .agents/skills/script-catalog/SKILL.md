---
name: script-catalog
description: For program maintenance ONLY (the user asked to change pipeline code). Find and reuse existing scripts before writing new ones. Never used during story production: production runs only Ai-iclone commands step by step.
---
# Script catalog — reuse first (maintainers only)

**Not for production.** While making a story part, the AI runs only the `Ai-iclone` commands the program prints (AGENTS.md, user rule 2026-11-28). Open this catalog only when the user asks to change the program itself.

1. Start with Ai-iclone.exe (no arguments), inspect the live story/part/step and rules card. Preview/CLI is the sole workflow controller.
2. Read `references/SCRIPT_CATALOG.md` in the installed plugin, or `docs/SCRIPT_CATALOG.md` in the repository. Search for the task before writing a script. The catalog covers the observed GitHub main and Windows working tree, not just filenames from an old skill snapshot.
3. Verify the exact file exists on the machine, read its current source, inputs, dependencies and side effects. For new or changed scripts, refresh the catalog; do not assume local-only files have been published or tested. Historical/specific scripts are not generic substitutes.
4. Reuse the generic script via the authorized current Preview stage. If a change is necessary, repair the existing helper narrowly, run appropriate tests, verify actual output. Never bypass dispatch/approval, create duplicate workflows, or claim completion based solely on a log.
5. Keep the catalog synchronized with GitHub and the installed plugin after additions, removals or changed functions. Do not publish story assets, local paths, keys, caches, progress or backup files. User-facing replies in Thai.
