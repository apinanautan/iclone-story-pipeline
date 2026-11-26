from pathlib import Path
import json,secrets
p=Path(__file__).resolve().parent
f=p/"relay.key"
if not f.exists():f.write_text(secrets.token_hex(32),encoding="ascii")
key=f.read_text().strip()
if len(key)<32:raise SystemExit("invalid local relay key")
(p/"config.local.js").write_text("const LOCAL_PREVIEW_KEY="+json.dumps(key)+";\n",encoding="utf-8")
print("Local relay configuration ready. Load unpacked extension in Chrome.")
