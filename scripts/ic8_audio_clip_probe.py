# Read-only inspection of avatar audio/viseme clip APIs and timing.
import os, json, RLPy
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
out={}
a=next(x for x in RLPy.RScene.GetAvatars() if x.GetName()=='p3_monk')
out['avatar']=a.GetName()
for attr in ('GetVisemeComponent','GetVoiceComponent','GetAudioComponent','GetFaceComponent'):
    try:
        c=getattr(a,attr)(); out[attr]={'type':str(type(c)),'methods':[m for m in dir(c) if any(q in m.lower() for q in ('clip','audio','voice','viseme','remove','time','key'))]}
        if c and hasattr(c,'GetClipCount'):
            out[attr]['count']=c.GetClipCount(); out[attr]['clips']=[]
            for i in range(c.GetClipCount()):
                cl=c.GetClip(i); row={'type':str(type(cl)),'methods':[m for m in dir(cl) if any(q in m.lower() for q in ('clip','time','audio','remove','trim','range','length','start','end','speed'))]}
                for meth in ('GetClipLength','GetClipStartTime','GetClipEndTime','GetStartTime','GetEndTime'):
                    try: row[meth]=getattr(cl,meth)().ToFloat()/6000.0
                    except Exception as e: row[meth+'Error']=str(e)
                out[attr]['clips'].append(row)
    except Exception as e: out[attr+'Error']=repr(e)
open(os.path.join(J,'audio_clip_probe.json'),'w').write(json.dumps(out,indent=2))
