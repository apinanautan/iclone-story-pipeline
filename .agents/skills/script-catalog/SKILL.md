---
name: script-catalog
description: Mandatory reusable script lookup and source verification before authoring or calling iClone Story Pipeline scripts; route the current Preview step to existing scripts and identify local-only or historical helpers.
---
# Script catalog — reuse first

1. Start with Ai-iclone.exe (no arguments), inspect the live story/part/step and rules card. Preview/CLI is the sole workflow controller.
2. Read `references/SCRIPT_CATALOG.md` in the installed plugin, or `docs/SCRIPT_CATALOG.md` in the repository. Search for the task before writing a script. The catalog covers the observed GitHub main and Windows working tree, not just filenames from an old skill snapshot.
3. Verify the exact file exists on the machine, read its current source, inputs, dependencies and side effects. For new or changed scripts, refresh the catalog; do not assume local-only files have been published or tested. Historical/specific scripts are not generic substitutes.
4. Reuse the generic script via the authorized current Preview stage. If a change is necessary, repair the existing helper narrowly, run appropriate tests, verify actual output. Never bypass dispatch/approval, create duplicate workflows, or claim completion based solely on a log.
5. Keep the catalog synchronized with GitHub and the installed plugin after additions, removals or changed functions. Do not publish story assets, local paths, keys, caches, progress or backup files. User-facing replies in Thai.
