"""Capture only the iClone window; optionally enqueue it for the bound chat."""
import argparse, ctypes, inspect, re
from ctypes import wintypes
from pathlib import Path
from PIL import ImageGrab, ImageStat
from queue_preview import STATE, queue
from bridge_binding import current

def capture(part=None):
    # part=None: any single iClone window, whatever project is open (Ai-iclone snap)
    user32=ctypes.windll.user32
    try: user32.SetProcessDPIAware()
    except OSError: pass
    candidates=[]
    cb=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
    @cb
    def visit(hwnd, lparam):
        if user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
            n=user32.GetWindowTextLengthW(hwnd)
            title=ctypes.create_unicode_buffer(n+1)
            user32.GetWindowTextW(hwnd,title,n+1)
            if title.value.startswith("iClone 8 - ") and (part is None or re.search(r"(?<![0-9.])"+re.escape(str(part))+r"\.iProject(?:\s*\*)?$",title.value)):
                candidates.append(hwnd)
        return True
    user32.EnumWindows(visit,0)
    if len(candidates)!=1: raise RuntimeError("Expected one visible iClone window"+("" if part is None else " for active part")+" (found %d)"%len(candidates))
    if "window" not in inspect.signature(ImageGrab.grab).parameters:
        raise RuntimeError("Pillow window capture is unavailable")
    im=ImageGrab.grab(window=candidates[0]).convert("RGB")
    if min(im.size)<200 or max(ImageStat.Stat(im).stddev)<6:
        raise RuntimeError("Blank or invalid window capture")
    im.thumbnail((1440,1000))
    STATE.mkdir(exist_ok=True)
    out=STATE/"capture_test.jpg"
    tmp=STATE/"capture_test.tmp"
    im.save(tmp,format="JPEG",quality=85)
    tmp.replace(out)
    print("CAPTURE OK",im.size,out.stat().st_size)
    return out

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--send",action="store_true")
    args=parser.parse_args()
    n=current();img=capture(n["part"])
    if args.send:
        print(queue(img,n["story"],str(n["part"]),kind="screen_review"))