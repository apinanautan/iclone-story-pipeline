"""Fixed iClone/RLPy watcher payload; copied atomically to the watcher run directory.

This file executes within iClone 8, not in the external MCP server process.
Input JSON lives at <__file__ base>.json and output at <base>.result.json.
"""
import json
import math
import os
import traceback
import RLPy

base = os.path.splitext(__file__)[0]
payload = json.load(open(base + ".json", encoding="utf-8"))
action = payload["action"]
a = payload["args"]


def T(seconds):
    return RLPy.RTime.FromValue(int(round(seconds * 6000)))


def obj(name, objects):
    found = [o for o in objects if o.GetName() == name]
    if len(found) != 1:
        raise ValueError("Object %r matches %d items (need exactly one)" % (name, len(found)))
    return found[0]


def pose(o):
    v = o.WorldTransform().T()
    return [round(v.x, 2), round(v.y, 2), round(v.z, 2)]


def set_transform(o, xyz, quat):
    ctrl = o.GetControl("Transform")
    v = RLPy.RTransform()
    ctrl.GetValue(T(0), v)
    v.T().x, v.T().y, v.T().z = xyz
    v.R().x, v.R().y, v.R().z, v.R().w = quat
    ctrl.SetValue(T(0), v)


def zq(deg):
    h = math.radians(deg) / 2
    return (0., 0., math.sin(h), math.cos(h))


def qmul(p, q):
    x,y,z,w = p; a,b,c,d = q
    return (w*a+x*d+y*c-z*b, w*b-x*c+y*d+z*a,
            w*c+x*b-y*a+z*d, w*d-x*a-y*b-z*c)


def look(at, to):
    dx,dy,dz = [to[i]-at[i] for i in range(3)]
    yaw = math.degrees(math.atan2(-dx,dy))
    pitch = math.atan2(dz,math.hypot(dx,dy))
    qp = (math.sin(pitch/2), 0., 0., math.cos(pitch/2))
    qf = (math.sin(math.pi/4), 0., 0., math.cos(math.pi/4))
    return qmul(zq(yaw), qmul(qp, qf))


def scene():
    out = {}
    for label, objs in (("avatars", RLPy.RScene.GetAvatars()),
                        ("props", RLPy.RScene.GetProps()),
                        ("cameras", RLPy.RScene.GetCameras()),
                        ("lights", RLPy.RScene.FindObjects(RLPy.EObjectType_Light))):
        out[label] = [{"name": o.GetName(), "position": pose(o)} for o in objs[:150]]
        out[label + "_total"] = len(objs)
    # Read-only camera API inspection for camera-switcher planning.
    out["switch_api"] = [v for v in dir(RLPy.RScene) if "Switch" in v]
    try:
        out["switch_frame_indices"] = len(RLPy.RScene.GetSwitchCameraFrameIndexs(RLPy.RGlobal.GetFps()))
    except Exception as ex:
        out["switch_frame_indices_error"] = str(ex)
    out["camera_controls"] = []
    for cam in RLPy.RScene.GetCameras():
        entry = {"name": cam.GetName()}
        try:
            entry["transform_key_count"] = cam.GetControl("Transform").GetKeyCount()
        except Exception as ex:
            entry["transform_error"] = str(ex)
        out["camera_controls"].append(entry)
    return out


def timeline():
    out = {"fps": RLPy.RGlobal.GetFps().ToFloat(),
           "end_time_ticks": RLPy.RGlobal.GetEndTime().ToFloat(),
           "end_seconds": RLPy.RGlobal.GetEndTime().ToFloat()/6000., "avatars": []}
    for av in RLPy.RScene.GetAvatars():
        sk = av.GetSkeletonComponent()
        if sk:
            fc = av.GetFaceComponent()
            faces = []
            for i in range(fc.GetClipCount() if fc else 0):
                try:
                    c = fc.GetClip(i)
                    faces.append({"start_seconds": round(c.ClipTimeToSceneTime(T(0)).ToFloat()/6000., 3),
                                  "clip_length_seconds": round(c.GetClipLength().ToFloat()/6000., 3),
                                  "speed": c.GetSpeed()})
                except Exception as e:
                    faces.append({"index": i, "read_error": str(e)})
            out["avatars"].append({"name": av.GetName(), "body_clip_count": sk.GetClipCount(),
                                   "face_clip_count": fc.GetClipCount() if fc else 0,
                                   "face_clips": faces})
    return out


def run():
    if action == "inspect_scene":
        return scene()
    if action == "inspect_timeline":
        return timeline()
    if action == "place_existing_avatar":
        av = obj(a["name"], RLPy.RScene.GetAvatars())
        set_transform(av, (a["x"], a["y"], a["z"]), zq(a["yaw"]))
        return {"avatar": av.GetName(), "position": pose(av)}
    if action == "set_project_duration":
        RLPy.RGlobal.SetProjectLength(T(a["seconds"]))
        RLPy.RGlobal.SetEndTime(T(a["seconds"]))
        return {"requested_seconds": a["seconds"], "end_seconds": RLPy.RGlobal.GetEndTime().ToFloat()/6000.}
    if action == "set_auto_blink":
        av = obj(a["name"], RLPy.RScene.GetAvatars())
        av.GetFaceComponent().SetAutoBlinkName("Normal")
        return {"avatar": av.GetName(), "blink": "Normal"}
    if action == "set_existing_camera":
        cam = obj(a["name"], RLPy.RScene.GetCameras())
        p, t = a["pos"], a["target"]
        set_transform(cam, p, look(p,t))
        cam.SetFocalLength(T(0), a["focal"])
        d = RLPy.RCameraDofData()
        d.SetEnable(a["dof"])
        if a["dof"]:
            dist = math.sqrt(sum((t[i]-p[i])**2 for i in range(3)))
            d.SetFocus(dist)
            d.SetRange(40)
            d.SetFarTransitionRegion(150)
            d.SetNearTransitionRegion(80)
            d.SetFarBlurScale(1)
            d.SetNearBlurScale(1)
        k = RLPy.RKey(); k.SetTime(T(0)); cam.AddDofKey(k, d)
        return {"camera": cam.GetName(), "position": pose(cam), "focal_mm": a["focal"], "dof": a["dof"]}
    if action == "apply_part2_face_lips":
        raise RuntimeError("Deprecated: no pre-cut WAV lip sync. Import full N.mp3 in iClone Voice/AccuLips and trim on Timeline.")
        # Face-only operation. Do not call RemoveAllAnimations, apply body motion,
        # reposition avatars, load .rlDikPreset or render anything.
        expected = {"p2_monk", "p2_im", "p2_old", "p2_woman", "p2_young", "p2_commf"}
        spoken = {
            "p2_old": ("p2_old.wav", 1.4),
            "p2_im": ("p2_im.wav", 13.4),
            "p2_woman": ("p2_woman.wav", 31.7),
            "p2_young": ("p2_young.wav", 40.8),
        }
        name = a["name"]
        if name not in expected:
            raise ValueError("Part 2 cast only")
        actors = RLPy.RScene.GetAvatars()
        if set(v.GetName() for v in actors) != expected:
            raise RuntimeError("Unexpected cast; refusing face modification")
        av = obj(name, actors)
        fc = av.GetFaceComponent()
        sk = av.GetSkeletonComponent()
        body_count_before = sk.GetClipCount()
        if body_count_before < 1:
            raise RuntimeError("AccuPOSE/body clip missing, refusing to continue")
        face_count_before = fc.GetClipCount()
        # iClone reserves a zero-length face clip at frame zero even when no iTalk exists.
        baseline_empty = (face_count_before == 1 and
                          fc.GetClip(0).GetClipLength().ToFloat() == 0)
        if face_count_before and not baseline_empty:
            raise RuntimeError("Existing non-empty face clips; refusing duplicate import")
        if abs(RLPy.RGlobal.GetEndTime().ToFloat() / 6000.0 - 86.5) > 0.01:
            raise RuntimeError("Part 2 timeline must be 86.5s")
        face_path = r"G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น\Digital Soul 100+\1.Watch\Look front.iTalk"
        if not os.path.isfile(face_path):
            raise FileNotFoundError("Look front.iTalk is missing")
        wav_path = None
        start = None
        if name in spoken:
            fn, start = spoken[name]
            wav_path = os.path.join(os.environ["LOCALAPPDATA"],
                "Tidmunz Studio", "snapgen_data", "ic8_jobs", fn)
            if not os.path.isfile(wav_path):
                raise FileNotFoundError(wav_path)
        RLPy.RScene.ClearSelectObjects()
        RLPy.RScene.SelectObject(av)
        times = []
        seconds = 0.0
        while seconds < 86.5 - 0.01:
            RLPy.RGlobal.SetTime(T(seconds))
            old_count = fc.GetClipCount()
            RLPy.RFileIO.LoadFile(face_path)
            new_count = fc.GetClipCount()
            if new_count == old_count + 1:
                clip = fc.GetClip(new_count - 1)
            elif seconds == 0 and baseline_empty and new_count == 1:
                # Some iClone builds replace the empty placeholder instead of appending.
                clip = fc.GetClip(0)
            else:
                raise RuntimeError("iTalk import did not append one facial clip")
            clip.SetSpeed(1.0)
            raw = clip.GetClipLength().ToFloat() / 6000.0
            if not 0.25 <= raw <= 90.0:
                raise RuntimeError("Unexpected Look front duration: %.2fs" % raw)
            clip.SetSpeed(0.5)
            times.append(round(seconds, 3))
            seconds += raw / 0.5
            if len(times) > 20:
                raise RuntimeError("Face import loop guard")
        fc.SetAutoBlinkName("Normal")
        if wav_path:
            RLPy.RAudio.LoadAudioToObject(av, wav_path, T(start))
        RLPy.RGlobal.SetTime(T(0))
        body_count_after = sk.GetClipCount()
        if body_count_before != body_count_after:
            raise RuntimeError("Body clip count changed from %d to %d" % (
                body_count_before, body_count_after))
        return {"avatar": name, "look_front_starts_seconds": times,
                "face_count_before": face_count_before,
                "face_count_after": fc.GetClipCount(),
                "body_count_before": body_count_before,
                "body_count_after": body_count_after,
                "blink": "Normal", "lip_wav": wav_path, "lip_start": start,
                "rendered": False, "saved": False}
    if action == "preview_camera_still":
        avs = RLPy.RScene.GetAvatars()
        if len(avs) != 6 or not all(v.GetName().startswith("p2_") for v in avs):
            raise RuntimeError("Unexpected Part 2 cast")
        cam = obj(a["name"], RLPy.RScene.GetCameras())
        RLPy.RGlobal.Stop()
        RLPy.RGlobal.SetTime(T(a["seconds"]))
        RLPy.RScene.SetCurrentCamera(cam)
        out = base + ".png"
        if os.path.exists(out):
            raise FileExistsError(out)
        status = RLPy.RGlobal.RenderImage(out)
        if not os.path.exists(out):
            raise RuntimeError("Preview image not produced: %s" % status)
        return {"camera": cam.GetName(), "at_seconds": a["seconds"],
                "preview_png": out, "file_bytes": os.path.getsize(out),
                "video_rendered": False}
    if action == "build_part2_camera_sequence":
        # Part 2 only. Camera transformations, switch keys and still previews.
        # Do not change any avatar animation, body pose, sound or lights.
        if abs(RLPy.RGlobal.GetEndTime().ToFloat()/6000. - 86.5) > 0.02:
            raise RuntimeError("Expected 86.5s project")
        if abs(RLPy.RGlobal.GetFps().ToFloat() - 60.) > 0.01:
            raise RuntimeError("Expected 60fps project")
        cast = {av.GetName(): av for av in RLPy.RScene.GetAvatars()}
        required = {"p2_monk","p2_im","p2_old","p2_young","p2_woman","p2_commf"}
        if set(cast) != required:
            raise RuntimeError("Unexpected cast; not keying cameras")
        before_body = {n: av.GetSkeletonComponent().GetClipCount() for n,av in cast.items()}
        before_face = {n: av.GetFaceComponent().GetClipCount() for n,av in cast.items()}
        if any(x != 1 for x in before_body.values()) or any(x != 3 for x in before_face.values()):
            raise RuntimeError("Unexpected body/face clips; not keying cameras")
        cameras = {cam.GetName(): cam for cam in RLPy.RScene.GetCameras()}
        if not {"Camera","Camera_0"}.issubset(set(cameras)):
            raise RuntimeError("Missing expected cameras")
        fps = RLPy.RGlobal.GetFps()
        previous = RLPy.RScene.GetSwitchCameraFrameIndexs(fps)
        if len(previous):
            raise RuntimeError("Existing switch-camera keys present; refusing to overwrite")
        # tuple(label, camera, first_frame, after_last_frame, mm, position, target, optional_end_position)
        shots = [
            ("old",        "Camera_0", 0,    420, 100, (310,586,25898),  (-97,586,25843), None),
            ("monk_early", "Camera",   420,  807, 100, (33,696,25910),   (33,896,25844),  None),
            ("im",         "Camera_0", 807, 1493, 100, (310,755,25904),  (-97,736,25843), None),
            ("ots_im",     "Camera",  1493, 1904,  80, (360,590,25912),  (-97,736,25844), None),
            ("woman",      "Camera_0",1904, 2449, 100, (-270,686,25906), (163,686,25844), None),
            ("young",      "Camera",  2449, 3048, 100, (340,436,25906),  (-97,436,25844), None),
            ("group",      "Camera_0",3048, 3229,  80, (720,235,26005),  (33,610,25854),  None),
            ("monk_push",  "Camera",  3229, 4530, 100, (33,696,25910),   (33,896,25844), (33,715,25910)),
            ("group_end",  "Camera_0",4530, 5190,  80, (700,845,26020),  (33,620,25856),  None)
        ]
        RLPy.RGlobal.Stop()
        def frame_time(frame):
            return RLPy.RTime.FromValue(frame*100) # 60fps=100 RTime ticks/frame
        def camera_key(cam, frame, xyz, tgt, mm, group):
            time = frame_time(frame)
            ctrl = cam.GetControl("Transform")
            transform = RLPy.RTransform()
            ctrl.GetValue(time, transform)
            p = transform.T()
            p.x,p.y,p.z = xyz
            q = look(xyz,tgt)
            r = transform.R()
            r.x,r.y,r.z,r.w = q
            st = ctrl.SetValue(time, transform)
            cam.SetFocalLength(time,mm)
            data = RLPy.RCameraDofData()
            data.SetEnable(True)
            dist = math.sqrt(sum((tgt[i]-xyz[i])**2 for i in range(3)))
            data.SetFocus(dist)
            data.SetRange(220 if group else 45)
            data.SetNearTransitionRegion(220 if group else 80)
            data.SetFarTransitionRegion(280 if group else 150)
            data.SetNearBlurScale(0.6 if group else 1)
            data.SetFarBlurScale(0.6 if group else 1)
            key = RLPy.RKey()
            key.SetTime(time)
            result = cam.AddDofKey(key,data)
            return str(st),str(result)
        keys = []
        for label, name, first, after, mm, xyz, target, end_pos in shots:
            cam = cameras[name]
            group = label.startswith("group")
            start_st = camera_key(cam,first,xyz,target,mm,group)
            end_st = camera_key(cam,after-1,end_pos or xyz,target,mm,group)
            keys.append({"shot":label,"start_frame":first,"end_frame":after-1,
                         "camera":name,"focal_mm":mm,"start_status":start_st,"end_status":end_st})
        if len(RLPy.RScene.GetSwitchCameraFrameIndexs(fps)) != 0:
            raise RuntimeError("Switcher unexpectedly changed during camera keying")
        RLPy.RScene.ClearSwitchCameraKeys()
        for label,name,first,after,mm,xyz,target,end_pos in shots:
            RLPy.RScene.AddSwitchCameraKey(frame_time(first), cameras[name])
        count = len(RLPy.RScene.GetSwitchCameraFrameIndexs(fps))
        if count != len(shots):
            raise RuntimeError("Switcher key count is %d, expected %d"%(count,len(shots)))
        images = []
        for idx,(label,name,first,after,mm,xyz,target,end_pos) in enumerate(shots):
            middle = first+(after-first)//2
            RLPy.RGlobal.SetTime(frame_time(middle))
            RLPy.RScene.SetCurrentCamera(cameras[name])
            img = base+"_shot%02d_%s.png"%(idx+1,label)
            if os.path.exists(img):
                raise FileExistsError(img)
            RLPy.RGlobal.RenderImage(img)
            if not os.path.exists(img) or os.path.getsize(img)<1000:
                raise RuntimeError("Preview missing: "+img)
            images.append({"shot":label,"at_frame":middle,"file":img,"bytes":os.path.getsize(img)})
        RLPy.RGlobal.SetTime(T(0))
        RLPy.RScene.SetCurrentCamera(cameras["Camera_0"])
        after_body = {n:av.GetSkeletonComponent().GetClipCount() for n,av in cast.items()}
        after_face = {n:av.GetFaceComponent().GetClipCount() for n,av in cast.items()}
        if before_body != after_body or before_face != after_face:
            raise RuntimeError("Avatar animation clip counts changed; review scene")
        return {"switch_key_count":count,"shots":keys,"previews":images,
                "before_body":before_body,"after_body":after_body,
                "before_face":before_face,"after_face":after_face,"saved":False,"rendered_video":False}
    if action == "retune_part2_group_shot":
        i = a["shot_index"]
        if i not in (7,9):
            raise ValueError("Group shot 7 or 9 only")
        indices = RLPy.RScene.GetSwitchCameraFrameIndexs(RLPy.RGlobal.GetFps())
        if len(indices) != 9:
            raise RuntimeError("Expected 9 camera switch keys")
        cam = obj("Camera_0",RLPy.RScene.GetCameras())
        start,end,mid = (3048,3228,3138) if i == 7 else (4530,5189,4860)
        xyz,tgt=a["pos"],a["target"]
        RLPy.RGlobal.Stop()
        for frame in (start,end):
            t = RLPy.RTime.FromValue(frame*100)
            ctrl = cam.GetControl("Transform")
            tr = RLPy.RTransform()
            ctrl.GetValue(t,tr)
            tr.T().x,tr.T().y,tr.T().z=xyz
            q=look(xyz,tgt)
            tr.R().x,tr.R().y,tr.R().z,tr.R().w=q
            ctrl.SetValue(t,tr)
            cam.SetFocalLength(t,80)
            d=RLPy.RCameraDofData()
            d.SetEnable(True)
            d.SetFocus(math.sqrt(sum((xyz[k]-tgt[k])**2 for k in range(3))))
            d.SetRange(220)
            d.SetNearTransitionRegion(220)
            d.SetFarTransitionRegion(280)
            d.SetNearBlurScale(0.6)
            d.SetFarBlurScale(0.6)
            key=RLPy.RKey()
            key.SetTime(t)
            cam.AddDofKey(key,d)
        RLPy.RGlobal.SetTime(RLPy.RTime.FromValue(mid*100))
        RLPy.RScene.SetCurrentCamera(cam)
        preview=base+"_group%02d.png"%i
        if os.path.exists(preview):
            raise FileExistsError(preview)
        RLPy.RGlobal.RenderImage(preview)
        if not os.path.isfile(preview) or os.path.getsize(preview)<1000:
            raise RuntimeError("Preview missing")
        return {"index":i,"camera":cam.GetName(),"at_frame":mid,"pos":xyz,
                "target":tgt,"png":preview,"bytes":os.path.getsize(preview),
                "switch_key_count":len(RLPy.RScene.GetSwitchCameraFrameIndexs(RLPy.RGlobal.GetFps()))}
    if action == "retune_part2_shot":
        i = a["shot_index"]
        if i not in range(1,10):
            raise ValueError("Invalid shot")
        if len(RLPy.RScene.GetSwitchCameraFrameIndexs(RLPy.RGlobal.GetFps())) != 9:
            raise RuntimeError("Expected nine switch keys before camera correction")
        cast = {v.GetName():v for v in RLPy.RScene.GetAvatars()}
        if set(cast) != {"p2_monk","p2_im","p2_old","p2_woman","p2_young","p2_commf"}:
            raise RuntimeError("Unexpected character list")
        before = {n:(v.GetSkeletonComponent().GetClipCount(),
                     v.GetFaceComponent().GetClipCount()) for n,v in cast.items()}
        segments=[(0,419),(420,806),(807,1492),(1493,1903),(1904,2448),
                  (2449,3047),(3048,3228),(3229,4529),(4530,5189)]
        start,end = segments[i-1]
        camname = "Camera_0" if i%2 else "Camera"
        cam = obj(camname,RLPy.RScene.GetCameras())
        xyz,tgt,mm = a["pos"],a["target"],a["focal"]
        RLPy.RGlobal.Stop()
        for frame in (start,end):
            tm = RLPy.RTime.FromValue(frame*100)
            ctrl = cam.GetControl("Transform")
            tr = RLPy.RTransform()
            ctrl.GetValue(tm,tr)
            tr.T().x,tr.T().y,tr.T().z=xyz
            q=look(xyz,tgt)
            tr.R().x,tr.R().y,tr.R().z,tr.R().w=q
            ctrl.SetValue(tm,tr)
            cam.SetFocalLength(tm,mm)
            data=RLPy.RCameraDofData()
            data.SetEnable(True)
            distance=math.sqrt(sum((xyz[k]-tgt[k])**2 for k in range(3)))
            data.SetFocus(distance)
            data.SetRange(45)
            data.SetNearTransitionRegion(80)
            data.SetFarTransitionRegion(150)
            data.SetNearBlurScale(1)
            data.SetFarBlurScale(1)
            key=RLPy.RKey()
            key.SetTime(tm)
            cam.AddDofKey(key,data)
        RLPy.RGlobal.SetTime(RLPy.RTime.FromValue((start+(end-start)//2)*100))
        RLPy.RScene.SetCurrentCamera(cam)
        out=base+"_shot%02d.png"%i
        if os.path.exists(out):
            raise FileExistsError("Preview output collision")
        RLPy.RGlobal.RenderImage(out)
        if not os.path.isfile(out) or os.path.getsize(out)<1000:
            raise RuntimeError("Preview missing")
        after={n:(v.GetSkeletonComponent().GetClipCount(),
                  v.GetFaceComponent().GetClipCount()) for n,v in cast.items()}
        if before!=after:
            raise RuntimeError("Character clips were modified unexpectedly")
        return {"shot":i,"camera":camname,"pos":xyz,"target":tgt,
                "focal":mm,"preview":out,"bytes":os.path.getsize(out),
                "cast_unchanged":True,"switch_keys":len(RLPy.RScene.GetSwitchCameraFrameIndexs(RLPy.RGlobal.GetFps()))}
    if action == "preview_part2_switcher":
        fps = RLPy.RGlobal.GetFps()
        count = len(RLPy.RScene.GetSwitchCameraFrameIndexs(fps))
        if count != 9:
            raise RuntimeError("Expected nine Switcher keys, found %d" % count)
        if abs(RLPy.RGlobal.GetEndTime().ToFloat()/6000.0 - 86.5) > 0.01:
            raise RuntimeError("Unexpected part duration")
        RLPy.RGlobal.Stop()
        results=[]
        for label,sec in (("old",2.0),("monk",10.0),("im",19.0),
                          ("woman",35.0),("commf",52.0),("monk_end",60.0),("final",81.0)):
            RLPy.RGlobal.SetTime(T(sec))
            current=RLPy.RScene.GetCurrentCamera()
            out=base+"_switch_"+label+".png"
            if os.path.exists(out):
                raise FileExistsError(out)
            RLPy.RGlobal.RenderImage(out)
            if not os.path.exists(out) or os.path.getsize(out)<1000:
                raise RuntimeError("Switcher still missing: "+label)
            results.append({"shot":label,"seconds":sec,
                            "current_camera":current.GetName() if current else None,
                            "preview":out,"bytes":os.path.getsize(out)})
        RLPy.RGlobal.SetTime(T(0))
        return {"switch_keys":count,"frames":results}
    if action == "inspect_part2_lip_sync":
        words=("viseme","lip","audio","voice","speech","phoneme","face")
        def relevant_methods(ob):
            return [x for x in dir(ob) if any(w in x.lower() for w in words) and not x.startswith("_")][:60]
        result={"r_audio_methods": relevant_methods(RLPy.RAudio),
                "rlpy_api_classes": [x for x in dir(RLPy) if any(w in x.lower() for w in ("viseme","voice","phoneme"))][:40],
                "avatars":[]}
        for av in RLPy.RScene.GetAvatars():
            fc=av.GetFaceComponent()
            item={"name":av.GetName(),"avatar_methods":relevant_methods(av),
                  "face_methods":relevant_methods(fc),
                  "face_clip_count":fc.GetClipCount(),
                  "body_clip_count":av.GetSkeletonComponent().GetClipCount()}
            for method in ("GetAudioComponent","GetVisemeComponent","GetVoiceComponent","GetSpeechComponent"):
                fn=getattr(av,method,None)
                if callable(fn):
                    try:
                        ob=fn()
                        item[method]={"present":bool(ob),"methods":relevant_methods(ob) if ob else []}
                        if method=="GetVisemeComponent" and ob is not None:
                            n=ob.GetClipCount()
                            item["viseme_clip_count"]=n
                            item["viseme_clips"]=[]
                            for index in range(min(n,20)):
                                try:
                                    clip=ob.GetClip(index)
                                    item["viseme_clips"].append({
                                        "index":index,
                                        "start_seconds":round(clip.ClipTimeToSceneTime(T(0)).ToFloat()/6000.,3),
                                        "duration_seconds":round(clip.GetClipLength().ToFloat()/6000.,3)})
                                except Exception as ex:
                                    item["viseme_clips"].append({"index":index,"error":str(ex)})
                    except Exception as ex:
                        item[method]={"error":str(ex)}
            result["avatars"].append(item)
        return result
    if action == "render_part":
        path = a["out"]
        # Defense in depth: never overwrite or write outside expected output.
        if os.path.normcase(os.path.abspath(path)) != os.path.normcase(os.path.abspath("E:/Video/%s.mp4" % a["part_number"])):
            raise ValueError("Invalid output path")
        if os.path.exists(path):
            raise FileExistsError(path)
        RLPy.RGlobal.SetRenderExportType(1)
        p = RLPy.RGlobal.GetRenderExportVideoParameter()
        p.strFormat = "MP4"
        p.kCommon.kFps = "60"
        p.kCommon.nOutputSizeWidth = 1920
        p.kCommon.nOutputSizeHeight = 1080
        p.kCommon.bFinalRender = True
        fps = RLPy.RGlobal.GetFps().ToFloat()
        p.kOutputRange.nOutputRangeStart = 0
        p.kOutputRange.nOutputRangeEnd = int(round(a["end_seconds"] * fps))
        try:
            p.bExportAudio = True
        except Exception:
            pass
        RLPy.RGlobal.SetRenderExportParameter(p)
        ret = RLPy.RGlobal.RenderVideo(path)
        return {"render_called": True, "output": path, "exists": os.path.exists(path), "return": str(ret)}
    raise ValueError("Unsupported action: %r" % action)


try:
    data = run()
    result = {"ok": True, "action": action, "data": data}
except Exception:
    result = {"ok": False, "action": action, "traceback": traceback.format_exc()[-8000:]}
with open(base + ".result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)
if not result["ok"]:
    raise RuntimeError(result["traceback"])
