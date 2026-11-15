# Restore the original AccuLips viseme keys saved from full-audio import + in-iClone trim.
# Source: %LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\monk_keys.json
# Expected rows: [scene_seconds, viseme_id, weight_fraction].
import json, os
import RLPy
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
rows=json.load(open(os.path.join(J,'monk_keys.json'),encoding='utf-8'))
a=next(x for x in RLPy.RScene.GetAvatars() if x.GetName()=='p3_monk')
v=a.GetVisemeComponent()
kv=v.GetVisemeKeys(); old=[kv[i] for i in range(len(kv))]
for k in old: v.RemoveVisemesKey(k)
added=0; errors=[]
for sec,vid,weight in rows:
    try:
        k=RLPy.RVisemeKey(); k.SetTime(RLPy.RTime.FromValue(int(round(sec*6000))))
        k.SetID(int(vid)); k.SetWeight(float(weight)*100.0)
        v.AddVisemeKey(k); added+=1
    except Exception as e: errors.append('%.3f id=%s: %r'%(sec,vid,e))
kv=v.GetVisemeKeys(); actual=[kv[i] for i in range(len(kv))]
times=[k.GetTime().ToFloat()/6000.0 for k in actual]
weights=[k.GetWeight() for k in actual]
open(os.path.join(J,'lip_restore.txt'),'w').write('removed %d restored %d actual %d range %.3f-%.3f weight %.3f-%.3f errors %s'%(len(old),added,len(actual),min(times) if times else -1,max(times) if times else -1,min(weights) if weights else -1,max(weights) if weights else -1,'; '.join(errors)))
