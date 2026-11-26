"""Headless analyzer wrapper, cache exact source + settings + analyzer revision. No proprietary iMotion decoding."""
import json,hashlib,subprocess,sys
from pathlib import Path
from blender_prop_build import blender
from cinematic_qa import digest,hashobj
ROOT=Path(__file__).resolve().parents[1]
def analyze(source,config):
    source=Path(source).resolve();config=Path(config).resolve()
    if source.suffix.lower()!=".blend" or not source.is_file():raise ValueError("provide transferred, saved animated .blend; DataLink/FBX transfer must be verified separately")
    c=json.loads(config.read_text(encoding="utf-8"))
    key=hashobj([digest(source),c,digest(ROOT/"scripts"/"blender_motion_analyze.py")])
    d=ROOT/"progress"/"motion_analysis";d.mkdir(parents=True,exist_ok=True);p=d/(key+".json")
    if not p.exists():
        t=d/(key+".partial.json")
        subprocess.run([blender(),"--background",str(source),"--threads","2","--python-exit-code","1","--python",str(ROOT/"scripts"/"blender_motion_analyze.py"),"--",str(config),str(t)],check=True)
        q=json.loads(t.read_text(encoding="utf-8"))
        if len(q.get("samples",[]))!=c["frames"][1]-c["frames"][0]+1:raise RuntimeError("incomplete frame samples")
        q.update(source_sha256=digest(source),settings_sha256=hashobj(c),cache_key=key)
        t.write_text(json.dumps(q,ensure_ascii=False),encoding="utf-8");t.replace(p)
    return p
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: motion_analyze.py transferred.blend bone_map.json")
    print(analyze(*sys.argv[1:]))
