# -*- coding: utf-8 -*-
"""Part 3 frame-accurate EDL/audio integrity guard. No scene mutation or render unless --assemble."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "data" / "part3_frame_edl.json"
FFMPEG_ROOT = Path(r"C:\Users\Apinan\AppData\Local\hermes\tools\ffmpeg-9.0.1-win32-x64\bin")
FFPROBE = FFMPEG_ROOT / "ffprobe.exe"
FFMPEG = FFMPEG_ROOT / "ffmpeg.exe"

def inspect_video(path):
    cmd = [str(FFPROBE), "-v", "error", "-select_streams", "v:0", "-show_entries",
           "stream=codec_name,codec_type,r_frame_rate,nb_frames,width,height,duration",
           "-of", "json", str(path)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if p.returncode: raise RuntimeError(f"ffprobe failed: {path}: {p.stderr}")
    streams = json.loads(p.stdout).get("streams") or []
    if len(streams) != 1: raise ValueError(f"No video stream: {path}")
    v = streams[0]
    fps = v.get("r_frame_rate")
    try: count = int(v["nb_frames"])
    except (ValueError, KeyError, TypeError): count = None
    return {"count": count, "fps":fps, "width":v.get("width"), "height":v.get("height"), "duration":v.get("duration")}

def validate(plan, media=False, require_ready=False):
    errors, warnings = [], []
    fps = int(plan["fps"])
    total = int(plan["total_video_frames"])
    wav = Path(plan["audio_source"])
    if not wav.is_file():
        errors.append(f"Missing source audio: {wav}")
    else:
        try:
            with wave.open(str(wav), "rb") as w:
                details = (w.getframerate(), w.getnframes())
                expected = (int(plan["audio_sample_rate"]), int(plan["audio_sample_frames"]))
                if details != expected: errors.append(f"WAV changed: {details}, expected {expected}")
                if w.getnchannels() != 2: errors.append("Original Part 3 audio must be stereo")
        except Exception as ex: errors.append(f"Unreadable WAV: {ex}")
    events = plan.get("events", [])
    if not events: errors.append("No events")
    pos = 0
    for e in events:
        ident = e.get("id", "?")
        start = int(e["start_frame"]); end = int(e["end_frame"])
        if start != pos: errors.append(f"{ident}: hole/overlap at frame {pos}->{start}")
        if end <= start: errors.append(f"{ident}: empty/reversed frame range")
        pos = end
        if require_ready and not e.get("visual_approved", False):
            errors.append(f"{ident}: user visual approval missing")
        if media:
            p = Path(e["video_path"])
            if not p.is_file():
                warnings.append(f"{ident}: video missing: {p}")
                if require_ready: errors.append(f"{ident}: video missing")
                continue
            info = inspect_video(p)
            if info["fps"] != f"{fps}/1": errors.append(f"{ident}: fps={info['fps']} expected {fps}/1")
            want = end-start
            offset = e.get("video_source_start_frame")
            if offset is None:
                warnings.append(f"{ident}: source frame offset NOT VERIFIED; cannot assemble")
                if require_ready: errors.append(f"{ident}: unknown source video start frame")
            elif info["count"] is not None and info["count"] < int(offset)+want:
                errors.append(f"{ident}: insufficient source video frames: have {info['count']}, need {int(offset)+want}")
            elif info["count"] is not None and info["count"] > int(offset)+want:
                warnings.append(f"{ident}: extra source frames: {info['count']}, assembly MUST trim to {want}")
            print(f"{ident}: file={p.name}, video={info['width']}x{info['height']} {info['fps']}, frames={info['count']}, use={want}, source_offset={offset}")
    if pos != total: errors.append(f"Coverage ends at {pos}, but original full video must end at {total}")
    if total*int(plan["audio_sample_rate"]) != int(plan["audio_sample_frames"])*fps:
        errors.append("Duration mismatch between WAV samples and video frame count")
    return errors, warnings

def assemble(plan, out):
    errors, warnings = validate(plan, media=True, require_ready=True)
    for w in warnings: print("WARN:",w)
    if errors: raise RuntimeError("Refused unsafe assembly:\n"+"\n".join(errors))
    if out.exists(): raise FileExistsError(f"Refusing to overwrite {out}")
    events=plan["events"]
    args=[str(FFMPEG),"-hide_banner","-loglevel","warning","-nostdin","-n"]
    for e in events: args+=["-i",e["video_path"]]
    args+=["-i",plan["audio_source"]]
    filters=[]
    for i,e in enumerate(events):
        start=int(e["video_source_start_frame"]); end=start+int(e["end_frame"])-int(e["start_frame"])
        filters.append(f"[{i}:v]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,fps={plan['fps']},scale=1920:1080,setsar=1,format=yuv420p[v{i}]")
    ins="".join(f"[v{i}]" for i in range(len(events)))
    filters.append(f"{ins}concat=n={len(events)}:v=1:a=0[v]")
    src=len(events)
    filters.append(f"[{src}:a]atrim=start_sample=0:end_sample={plan['audio_sample_frames']},asetpts=PTS-STARTPTS[a]")
    args += ["-filter_complex",";".join(filters),"-map","[v]","-map","[a]","-c:v","libx264","-preset","medium","-crf","18","-r",str(plan["fps"]),"-frames:v",str(plan["total_video_frames"]),"-c:a","aac","-b:a","192k","-ar","48000","-ac","2","-movflags","+faststart",str(out)]
    print("Assembling original continuous audio with exact 2022 video frames, no segment audio.")
    subprocess.run(args, check=True)
    probe=inspect_video(out)
    if probe["count"] != plan["total_video_frames"]: raise RuntimeError(f"Output frame count wrong: {probe}")
    print("ASSEMBLED:",out)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--plan",type=Path,default=DEFAULT_PLAN)
    a.add_argument("--audit",action="store_true",help="Inspect existing event videos and WAV; no output modification")
    a.add_argument("--assemble",action="store_true",help="EXPLICITLY render master; requires every event approved")
    a.add_argument("--output",type=Path,default=Path(r"E:\Video\3_event_master_20261111.mp4"))
    args=a.parse_args()
    p=json.loads(args.plan.read_text(encoding="utf-8-sig"))
    if args.assemble:
        assemble(p,args.output)
        return
    errors,warnings=validate(p,media=args.audit,require_ready=False)
    for e in p["events"]:
        print(f"{e['id']}: [{e['start_frame']},{e['end_frame']})={e['end_frame']-e['start_frame']} frames = {(e['end_frame']-e['start_frame'])/p['fps']:.3f}s; approved={e.get('visual_approved',False)}")
    for w in warnings: print("WARN:",w)
    for e in errors: print("ERROR:",e)
    print("PLAN", "PASS" if not errors else "FAIL")
    return 1 if errors else 0

if __name__=="__main__": sys.exit(main())
