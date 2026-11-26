# Runs inside iClone with existing ic8_cams helper definitions (not its main job).
from pathlib import Path
cfg=json.load(open(os.path.join(J,"scene_review_request.json"),encoding="utf-8"))
folder=Path(cfg["directory"]);old=RLPy.RScene.GetCurrentCamera();oldtime=RLPy.RGlobal.GetTime()
before={c.GetID() for c in RLPy.RScene.GetCameras()};created=[];views=[];result={"ok":False}
try:
    RLPy.RFileIO.LoadFile(ICAM);QtWidgets.QApplication.processEvents();time.sleep(.3)
    created=[c for c in RLPy.RScene.GetCameras() if c.GetID() not in before]
    if len(created)!=1:raise RuntimeError("survey camera not uniquely created")
    cam=created[0];cam.SetName("AI_SceneSurvey_Temporary");RLPy.RGlobal.RemoveAllAnimations(cam)
    actors=[a for a in RLPy.RScene.GetAvatars() if a.GetName() in cfg["cast"]]
    if len(actors)!=len(cfg["cast"]):raise RuntimeError("missing staged cast")
    shots=cfg["shots"];count=min(5,len(shots))
    indices=sorted(set(round(i*(len(shots)-1)/max(1,count-1)) for i in range(count)))
    for i,idx in enumerate(indices):
        sh=shots[idx];t=sum(sh["t"])/2;settle(t);bounds=[]
        for a in actors:
            if not a.IsVisible(T(t)):continue
            mx,c,mn=RLPy.RVector3(),RLPy.RVector3(),RLPy.RVector3();a.GetBounds(mx,c,mn)
            bounds.append(([mn.x,mn.y,mn.z],[mx.x,mx.y,mx.z],a.GetName()))
        if bounds:
            low=[min(b[0][k] for b in bounds) for k in range(3)];high=[max(b[1][k] for b in bounds) for k in range(3)]
            target=[(low[k]+high[k])/2 for k in range(3)]
            radius=max(220,math.hypot(high[0]-low[0],high[1]-low[1])*1.5,(high[2]-low[2])*1.6)
        else:
            target=sh["target"];radius=max(220,math.dist(sh["pos"],target))
        for deg in (0,90,180,270):
            ang=math.radians(deg);pos=[target[0]+radius*math.cos(ang),target[1]+radius*math.sin(ang),target[2]+60]
            room=cfg.get("room")
            if room and len(room)==4:
                pos[0]=max(room[0]+10,min(room[2]-10,pos[0]));pos[1]=max(room[1]+10,min(room[3]-10,pos[1]))
            key(cam,t,pos,target,35);dof(cam,t,pos,target,False)
            RLPy.RScene.SetCurrentCamera(cam);settle(t)
            if math.dist(campos(cam,t),pos)>3 or RLPy.RScene.GetCurrentCamera().GetID()!=cam.GetID():raise RuntimeError("survey camera mismatch")
            name=f"scene_{i+1:02d}_{deg:03d}.png"
            RLPy.RGlobal.RenderImage(str(folder/name));settle(t)
            if not (folder/name).is_file():raise RuntimeError("survey image missing")
            views.append({"file":name,"time":t,"angle":deg,"pos":pos,"target":target,"bounds":bounds})
    result={"ok":True,"views":views}
except Exception as e:result={"ok":False,"error":str(e)}
finally:
    try:
        if old is not None:RLPy.RScene.SetCurrentCamera(old)
        for c in created:RLPy.RScene.RemoveObject(c)
        RLPy.RGlobal.SetTime(oldtime);QtWidgets.QApplication.processEvents()
    except Exception as e:result={"ok":False,"error":"restore failed: "+str(e)}
    (folder/"scene_capture.json").write_text(json.dumps(result,ensure_ascii=False),encoding="utf-8")
