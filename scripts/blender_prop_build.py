from pathlib import Path
import os,sys,subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def blender():
    from shutil import which
    found=which("blender")
    if found:return found
    paths=sorted((Path(os.environ.get("ProgramFiles","C:/Program Files"))/"Blender Foundation").glob("Blender */blender.exe"),reverse=True)
    if not paths:raise RuntimeError("Blender executable missing; run doctor")
    return str(paths[0])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(source,folder):
    source=Path(source).resolve();folder=Path(folder).resolve()
    # New workspace only; never run in the user's open Blender project.
    if not source.is_file() or source.suffix!=".py":raise ValueError("provide authored local .py source")
    if folder.exists():raise ValueError("use a NEW versioned output folder")
    folder.mkdir(parents=True)
    authored=folder/"model_source.py";authored.write_bytes(source.read_bytes())
    skill=Path.home()/".codex"/"skills"/"blender-asset-qa"/"scripts"
    if not (skill/"qa_check.py").is_file():raise RuntimeError("installed blender-asset-qa skill missing")
    args=[blender(),"--background","--factory-startup","--threads","2","--python-exit-code","1","--python",str(authored),"--",str(folder)]
    with (folder/"build.log").open("w",encoding="utf-8") as log:
        subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True,cwd=folder)
    blend=folder/"model.blend"
    if not blend.is_file():raise RuntimeError("authored script must save model.blend")
    with (folder/"qa.log").open("w",encoding="utf-8") as log:
        subprocess.run([blender(),"--background",str(blend),"--threads","2","--python-exit-code","1","--python",str(ROOT/"scripts"/"blender_prop_export.py"),"--",str(folder),str(skill)],stdout=log,stderr=subprocess.STDOUT,check=True,cwd=folder)
    q=json.loads((folder/"asset_qa.json").read_text(encoding="utf-8"))
    if q.get("pass") is not True:raise RuntimeError("asset QA rejected; inspect asset_qa.json")
    f=folder/"model.fbx"
    if not f.is_file() or not f.stat().st_size:raise RuntimeError("FBX export missing")
    receipt={"fbx":str(f),"fbx_sha256":sha(f),"blend_sha256":sha(blend),"qa_sha256":sha(folder/"asset_qa.json"),"geometry_pass":True,"visual_review":"required in Blender and iClone"}
    (folder/"asset_receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding="utf-8")
    print("OK asset generated + geometry QA; visually inspect before import:",f)
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: blender_prop_build.py <authored.py> <new output folder>")
    run(sys.argv[1],sys.argv[2])
