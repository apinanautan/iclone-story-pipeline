# Explicit silent NONE keys; preserve existing speech keys.
import RLPy, os, json
WIN=json.loads(os.environ['LIPWIN'])
END=float(WIN.pop('__end__'))
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
def keys(v):
    kv=v.GetVisemeKeys()
    return [kv[i] for i in range(len(kv))]
def sec(k):return k.GetTime().ToFloat()/6000.
def row(k):return [round(sec(k),5),int(k.GetID()),float(k.GetWeight())]
out=[];audit={};pending=[]
for a in RLPy.RScene.GetAvatars():
    n=a.GetName()
    if n not in WIN:continue
    v=a.GetVisemeComponent();old=keys(v);w=[]
    for s,e in sorted(WIN[n]):
        if w and s<=w[-1][1]+.001:w[-1][1]=max(w[-1][1],e)
        else:w.append([s,e])
    spoken=[row(k) for k in old if any(s<=sec(k)<=e for s,e in w) and k.GetID()!=0]
    if w and not spoken:raise RuntimeError(n+' no speech keys')
    pending.append((a,v,old,w,spoken))
    audit[n]={'before':[row(k) for k in old],'windows':w}
with open(os.path.join(J,'lip_silence_before.json'),'w',encoding='utf-8') as f:json.dump(audit,f,ensure_ascii=False)
for a,v,old,w,spoken in pending:
    n=a.GetName();inside=lambda t:any(s<=t<=e for s,e in w)
    for k in old:
        if not inside(sec(k)):v.RemoveVisemesKey(k)
    gaps=[];last=0.
    for s,e in w:
        if s>last:gaps.append((last,s))
        last=e
    if END>last:gaps.append((last,END))
    if w:
        times=set()
        for lo,hi in gaps:
            l=lo+(1/60 if lo else 0);h=hi-(1/60 if hi<END else 0)
            if l>h:continue
            times.update([round(l,5),round(h,5)])
            x=l+1
            while x<h:times.add(round(x,5));x+=1
        for t in sorted(times):
            k=RLPy.RVisemeKey();k.SetID(0);k.SetWeight(100.0);k.SetTime(T(t));v.AddVisemeKey(k)
    actual=[row(k) for k in keys(v)]
    after=[r for r in actual if r[1]!=0 and inside(r[0])]
    if sorted(after)!=sorted(spoken):raise RuntimeError(n+' speech keys changed')
    if any(r[1]!=0 and not inside(r[0]) for r in actual):raise RuntimeError(n+' non-neutral outside speech')
    audit[n]['after']=actual
    fc=a.GetFaceComponent()
    try:
        names=[x for g in ('Jaw','MouthBase','MouthMove') for x in fc.GetExpressionNames(g) if any(y in x.lower() for y in ('open','close','drop','press','clench'))]
        samples=[round((lo+hi)/2,3) for lo,hi in gaps if hi-lo>.5]+[round((lo+hi)/2,3) for lo,hi in w]
        audit[n]['face_names']=names
        audit[n]['face_weights']={str(t):list(fc.GetExpressionWeights(T(t),names)) for t in samples}
    except Exception as e:audit[n]['face_probe_error']=repr(e)
    out.append('%s speech keys preserved %d; total %d; non-neutral outside speech 0'%(n,len(spoken),len(actual)))
with open(os.path.join(J,'lip_silence_after.json'),'w',encoding='utf-8') as f:json.dump(audit,f,ensure_ascii=False)
open(os.path.join(J,'lip_trim.txt'),'w',encoding='utf-8').write(chr(10).join(out))
