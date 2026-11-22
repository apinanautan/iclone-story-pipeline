# MCP state (2026-11-22)

Rebuilt as a thin wrapper over Ai-iclone (`scripts/ai_iclone.py`): 10 tools, one Ai-iclone command each, same step
1..N flow for every part. The old ~20 fixed tools (many hard-coded for part 2) and `iclone_job.py` were removed.

Verified 2026-11-22: real MCP stdio initialize + tools/list (10 tools) + call `status` OK; empty `approve` refused;
`--cli status` / `--cli do_next_step {"dry": true}` OK; `tests/test_mcp_server.py` 4/4. No iClone was driven.

Optional OpenPlugin auto-start of the watcher (`openplugin/main.py`, `install_openplugin.cmd`) is unchanged.
