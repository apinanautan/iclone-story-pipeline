"""Explicit, per-achievement stop mailbox; independent of production status."""
import argparse,json,os,re,time,uuid
from pathlib import Path
STATE=Path(__file__).resolve().parent.parent/"preview_bridge_local"/"goal_signals"

def code_key(code):
    code=str(code).strip().upper()
    if code.startswith("ACHIEVEMENT:"):code=code.split(":",1)[1].strip()
    if not re.fullmatch(r"[A-F0-9]{8}-[A-F0-9]{3}",code):raise ValueError("invalid achievement code")
    return code

def read(code):
    p=STATE/(code_key(code)+".json")
    try:return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:return {}

def write(code,d):
    STATE.mkdir(parents=True,exist_ok=True)
    p=STATE/(code_key(code)+".json")
    t=p.with_name(p.name+"."+uuid.uuid4().hex+".tmp")
    t.write_text(json.dumps(d),encoding="utf-8");os.replace(t,p)

def request(code):
    k=code_key(code);d=read(k)
    if d.get("state") in ("requested","stopped"):return d
    d={"state":"requested","id":uuid.uuid4().hex,"time":time.time()}
    write(k,d);return d

def acknowledge(code,id,session):
    d=read(code)
    if d.get("id")!=id or d.get("state") not in ("requested","stopped"):raise ValueError("unknown stop request")
    if not isinstance(session,str) or not 1<=len(session)<=100:raise ValueError("invalid session")
    if d["state"]=="stopped":
        if d.get("session")!=session:raise ValueError("wrong session")
        return d
    d.update(state="stopped",session=session,ack_time=time.time());write(code,d);return d

def main():
    p=argparse.ArgumentParser(description="Stop the exact Goal Tracker achievement, not iClone.")
    p.add_argument("code");p.add_argument("--wait",type=float,default=35)
    a=p.parse_args();code=code_key(a.code);d=request(code)
    # The tracker checks every 30 s; a request it has not picked up yet still stops it on its next check.
    end=time.monotonic()+max(0,min(a.wait,40))
    while d.get("state")!="stopped" and time.monotonic()<end:
        time.sleep(.25);d=read(code)
    print(json.dumps(d))
    print("หยุดตัวติดตามแล้ว" if d.get("state")=="stopped" else "ส่งคำขอหยุดแล้ว ตัวติดตามจะหยุดในรอบตรวจถัดไป (ไม่เกิน 30 วินาที) ไม่ต้องรันซ้ำ")
    return 0

if __name__=="__main__":raise SystemExit(main())
