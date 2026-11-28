"""Inventory native Timeline audio. Hidden/unclassified audio fails closed."""
import json
import os
import re

CLIP = re.compile(r"^(.*?)\s+\((\d+(?:\.\d+)?)%\)")
AUDIO_HINT = re.compile(r"Embedded Timecode|\.(?:wav|mp3|ogg|flac|m4a|wma|aac)\b", re.I)
AUDIO_EXT = re.compile(r"\.(?:wav|mp3|ogg|flac|m4a|wma|aac)\b", re.I)
MOTION_META = re.compile(r"Time Warp\s*:", re.I)

def classify(rows, items):
    audio_rows = {round(r["y"], 2) for r in rows if r["visible"] and r["name"] in ("Sound", "Voice")}
    project_sound = None
    for r in sorted(rows, key=lambda r:r["y"]):
        if not r["visible"]:continue
        if r["name"] == "Project":project_sound = "pending"
        elif project_sound == "pending" and r["name"] == "Sound":
            project_sound = round(r["y"],2);break
    clips=[];uncertain=[]
    for i in items:
        m=CLIP.match(i["tip"])
        if not m:
            if AUDIO_HINT.search(i["tip"]):uncertain.append(i)
            continue
        on_audio=i["visible"] and round(i["y"],2) in audio_rows
        if on_audio and i["selectable"]:
            clips.append(dict(i,name=m.group(1),speed=float(m.group(2)),project=round(i["y"],2)==project_sound))
        elif not on_audio and MOTION_META.search(i["tip"]) and not AUDIO_EXT.search(i["tip"]):
            continue  # native motion metadata, not a sound clip
        elif on_audio or AUDIO_HINT.search(i["tip"]):
            uncertain.append(i)
    return {"project_sound":project_sound if isinstance(project_sound,(float,int)) else None,"clips":clips,"uncertain":uncertain}

def single_correct(report, name):
    clips=report["clips"]
    return (report["project_sound"] is not None and not report["uncertain"] and len(clips)==1
            and clips[0]["project"] and clips[0]["name"]==name and abs(clips[0]["x"])<0.01
            and clips[0]["speed"]==100)

def run(mode):
    import RLPy
    from PySide2 import QtWidgets
    from shiboken2 import isValid
    app=QtWidgets.QApplication.instance()
    main=next(w for w in app.allWidgets() if isValid(w) and w.objectName()=="iClone6 MainWindow")
    T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
    J=os.path.join(os.environ["LOCALAPPDATA"],"Tidmunz Studio","snapgen_data","ic8_jobs")
    if mode=="prepare":
        RLPy.RGlobal.Stop()
        for a in RLPy.RScene.GetAvatars():
            v=a.GetVisemeComponent()
            for _ in range(v.GetClipCount()):
                before=v.GetClipCount()
                cl=v.GetClip(0);start=cl.ClipTimeToSceneTime(T(0)).ToFloat()/6000
                length=cl.GetClipLength().ToFloat()/6000
                if length<=0:raise RuntimeError("invalid voice clip "+a.GetName())
                v.RemoveVisemesClip(T(start+min(1,length/2)))
                if v.GetClipCount()!=before-1:raise RuntimeError("voice clip removal not verified "+a.GetName())
        RLPy.RGlobal.SetTime(T(0));app.processEvents()
    if mode=="prepare":
        # Preserve the native Project track selection. Sound action is a toggle,
        # not an idempotent reveal, and the button is not checkable.
        for w in app.allWidgets():
            if isValid(w) and w.objectName()=="qtLeftGraphicsView" and w.isVisible():
                scene=w.scene()
                rows=[{"name":i.toolTip(),"y":i.scenePos().y(),"visible":i.isVisible()} for i in scene.items() if isValid(i) and i.toolTip() in ("Project","Sound","Voice","Switcher")]
                if classify(rows,[])["project_sound"] is not None:return
        next(a for a in main.actions() if a.objectName()=="qtOpenSoundTrackAction").trigger()
        return
    if mode=="reveal":
        next(a for a in main.actions() if a.objectName()=="qtShowAllAudioTrackAction").trigger()
        return
    rows=[];items=[];refs={};right=None;right_scene=None
    seen=set()
    for w in app.allWidgets():
        if not isValid(w) or not w.isVisible():continue
        name=w.objectName()
        if name not in ("qtLeftGraphicsView","qtMainGraphicsView"):continue
        if name in seen:raise RuntimeError("multiple visible timeline views: "+name)
        scene=w.scene()
        if not isValid(scene):raise RuntimeError("invalid timeline scene: "+name)
        for i in scene.items():
            if not isValid(i):continue
            tip=i.toolTip()
            if name=="qtLeftGraphicsView":
                if tip in ("Project","Sound","Voice","Switcher","Music","Background Music"):
                    rows.append({"name":tip,"y":i.scenePos().y(),"visible":i.isVisible()})
            elif CLIP.match(tip) or AUDIO_HINT.search(tip):
                k=len(items);refs[k]=i
                items.append({"id":k,"tip":tip,"y":i.scenePos().y(),"x":i.pos().x(),"visible":i.isVisible(),"selectable":bool(int(i.flags())&2)})
        seen.add(name)
        if name=="qtMainGraphicsView":right,right_scene=w,scene
    if seen!={"qtLeftGraphicsView","qtMainGraphicsView"}:raise RuntimeError("incomplete visible timeline")
    report=classify(rows,items)
    report["visemes"]={a.GetName():a.GetVisemeComponent().GetClipCount() for a in RLPy.RScene.GetAvatars()}
    report["selected"]=0
    if mode=="select":
        if report["project_sound"] is None or report["uncertain"] or any(report["visemes"].values()):
            raise RuntimeError("audio inventory incomplete; do not delete or import")
        right_scene.clearSelection()
        for c in report["clips"]:refs[c["id"]].setSelected(True)
        chosen=right_scene.selectedItems()
        if len(chosen)!=len(report["clips"]) or any(not refs[c["id"]].isSelected() for c in report["clips"]):
            raise RuntimeError("audio selection not verified")
        right.setFocus()
        report["selected"]=len(chosen)
    with open(os.path.join(J,"sound_tracks.json"),"w",encoding="utf-8") as f:
        json.dump(report,f,ensure_ascii=False,indent=2)

if __name__=="__main__":
    run(SOUND_MODE)
