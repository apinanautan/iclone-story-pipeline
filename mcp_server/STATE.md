# MCP implementation state (2026-11-07)

Objective: Add iClone Story Pipeline MCP and Dino Tunnel CLI, plus an optional safe OpenPlugin auto-start.

Verified on DESKTOP-F1PJT4S: Windows Python 3.13 with installed MCP SDK; 14 MCP tools discovered via real stdio `initialize` and `tools/list`; real MCP tool call `get_project_status` succeeded; offline tests 5/5 pass; CLI status/job inspection works. Read-only scene probe `mcp_adc3027d25962a5f` completed with watcher `.done`, inner result `ok: true`, 6 avatars, 7 props, 2 cameras, 13 lights. No scene-modifying MCP calls or render have been executed.

Safety incident: existing stale watcher job `clr.py` would attempt direct `.rlDikPreset` load and was preserved as `clr.py.unsafe-hold-20261107` in the watcher run folder. Do not run it.

OpenPlugin startup: source staged under `mcp_server/openplugin/main.py` and one-click UAC installer staged as `mcp_server/install_openplugin.cmd`; Program Files install attempt from current unprivileged remote session failed (Access Denied); tool admin execution also unavailable. User approval of Windows UAC is required to finish optional auto-start. Do not restart current iClone if unsaved work is present. Verify `mcp_autostart_status.txt` and an actual completed read-only job on next normal launch.

No audio import, scene modifications, project saves, video rendering, forced app restarts, public network exposure, or G: writes by this MCP implementation.

Remaining: optional user-approved UAC installer, auto-start verification after next normal iClone launch, tests for scene mutations/render only when requested. ChatGPT web reaches these tools through existing Dino Tunnel CLI, not a direct network MCP endpoint.
