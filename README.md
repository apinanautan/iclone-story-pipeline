# iClone Story Pipeline MCP Server

Runs on the existing Windows machine alongside iClone 8; reuses `scripts/ic8_watch.py` and its job queue. No iClone UI changes and no API keys required for **local stdio**.

## One command (Dino Tunnel / PowerShell)

```powershell
py -3 "C:\Users\Apinan\Documents\iClone Story Pipeline\mcp_server\server.py" --cli get_project_status
py -3 "C:\Users\Apinan\Documents\iClone Story Pipeline\mcp_server\server.py" --cli inspect_scene
py -3 "C:\Users\Apinan\Documents\iClone Story Pipeline\mcp_server\server.py" --cli get_job_result mcp_xxxxxxxxxxxxxxxx
```

## MCP client configuration (local desktop clients)

```json
{
  "mcpServers": {
    "iclone-story": {
      "command": "C:\\Windows\\py.exe",
      "args": ["-3", "C:\\Users\\Apinan\\Documents\\iClone Story Pipeline\\mcp_server\\server.py"]
    }
  }
}
```

This uses Python's installed `mcp` library (`from mcp.server.fastmcp import FastMCP`).

For debugging, `--http` starts **localhost only** on `127.0.0.1:8766/mcp`, **without network authentication**. Do not expose/port-forward this endpoint publicly. On ChatGPT web, a local stdio MCP server is not directly reachable; use the existing authorized Dino Tunnel shell path and `--cli` until a secure, authenticated MCP tunnel endpoint is provisioned. Never claim the local package alone is a cloud connection.

## Safety

- `get_project_status`, `list_project_files`, `read_project_file`, `get_rules`, `list_jobs`, `get_job_result`, `verify_part_output` are read-only.
- `inspect_scene`, `inspect_timeline` queue non-scene-changing probes. Results appear through `get_job_result` only **after watcher execution**; a stale `watcher.alive` file does not prove watcher health.
- `place_existing_avatar`, `set_auto_blink`, `set_existing_camera`, `set_project_duration` require `confirm_change=true` after the user requests the change.
- `render_part` requires `confirm_render=true` after explicit user instruction, targets `E:\Video\N.mp4` only, and refuses to overwrite. Rendering may take time and may produce full project length regardless of requested range; verify output after completion.
- No script upload or arbitrary code execution API is exposed. No G: writes, no Save As, no deleting scene objects. Saving projects still requires the verified GUI workflow.
- Loading `scripts/ic8_watch.py` **once after each iClone restart** is still required. `watcher.alive` alone is a startup marker, not a continuous heartbeat.

## Source map

`mcp_server/server.py` — typed MCP tools and Dino Tunnel command-line adapter.

`mcp_server/iclone_job.py` — fixed RLPy job payload copied atomically to watcher queue.

`tests/test_mcp_server.py` — read-only and fake-queue safety tests (does not require iClone running).

`mcp_server/STATE.md` — implementation/test status.

## Optional automatic watcher startup

`mcp_server/openplugin/main.py` is a small iClone OpenPlugin auto-loader. To enable:

1. **Double-click** `mcp_server/install_openplugin.cmd` and approve the Windows administrator/UAC prompt. This copies the bridge to `C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\iCloneStoryBridge\main.py`. If Windows elevation is denied, leave the file staged and start watcher manually.
2. **Do not restart iClone just to test** if the current scene is unsaved. On the *next normal launch*, iClone attempts to initialize the plugin, which starts the existing watcher only when the watcher run directory has no pending `.py` jobs.
3. After launch, inspect `%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\mcp_autostart_status.txt` and run a harmless `inspect_scene` with `get_job_result` to verify actual execution. Installation alone doesn't prove startup worked.

If a pending `.py` job exists at startup, the auto-loader **refuses to start** until the queue is manually reviewed; it does not silently run old jobs. A dangerous stale `clr.py` containing the known `.rlDikPreset` crash-inducing call was preserved under `.unsafe-hold-20261107` during this installation. Do not run it. The read-only scene probe subsequently completed successfully, confirming the watcher and RLPy bridge were operational. The auto-loader installer still needs user-approved UAC because the current remote shell cannot write to Program Files.
