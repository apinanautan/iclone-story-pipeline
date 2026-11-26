import subprocess,json,math
def validate_streams(data,want):
    out={}
    for kind in ("video","audio"):
        candidates=[s for s in data.get("streams",[]) if s.get("codec_type")==kind]
        if not candidates:raise ValueError("missing "+kind+" stream")
        try:dur=float(candidates[0]["duration"])
        except (KeyError,TypeError,ValueError):raise ValueError("missing "+kind+" stream duration")
        if not math.isfinite(dur) or dur<=0 or dur+.05<want:raise ValueError(f"{kind} stream {dur:.3f}s shorter than source {want:.3f}s")
        out[kind]=dur
    return out
def probe_video(ffprobe,path,want):
    r=subprocess.run([ffprobe,"-v","error","-show_entries","stream=codec_type,duration","-of","json",str(path)],capture_output=True,text=True,check=True,timeout=30)
    return validate_streams(json.loads(r.stdout),want)
