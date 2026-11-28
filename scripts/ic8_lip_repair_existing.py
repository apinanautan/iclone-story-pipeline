import RLPy,os,json
from pathlib import Path
j=Path(os.environ['LOCALAPPDATA'])/'Tidmunz Studio'/'snapgen_data'/'ic8_jobs'
ref=json.loads((j/'lip6_original_1040_keys.json').read_text(encoding='utf8'))
win=json.loads(os.environ['LIPWIN']); end=win.pop('__end__')
assert set(ref)==set(win) and all(ref[n]['windows']==win[n] for n in win)
def live(v):
 k=v.GetVisemeKeys()
 return [k[i] for i in range(len(k))]
def row(k):return [round(k.GetTime().ToFloat()/6000.,5),int(k.GetID()),float(k.GetWeight())]
out={}; lines=[]
for a in RLPy.RScene.GetAvatars():
 n=a.GetName()
 if n not in win:continue
 v=a.GetVisemeComponent(); w=win[n]
 inside=lambda r:any(s<=r[0]<=e for s,e in w)
 speech=sorted(r for r in ref[n]['before'] if r[1]!=0 and inside(r))
 current=[row(k) for k in live(v)]
 assert sorted(r for r in current if r[1]!=0 and inside(r))==speech,n+' original speech mismatch'
 extras=[r for r in current if r[1]!=0 and not inside(r)]
 out[n]={'before':ref[n]['before'],'windows':w,'repair_before':current,'extras_before':extras}
 (j/'lip6_repair_progress.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')
 # Re-fetch the key before each removal: native collection changes after mutation.
 for target in extras:
  candidates=[k for k in live(v) if row(k)==target]
  if not candidates:continue
  v.RemoveVisemesKey(candidates[0])
 actual=[row(k) for k in live(v)]
 assert sorted(r for r in actual if r[1]!=0 and inside(r))==speech,n+' speech changed'
 assert not any(r[1]!=0 and not inside(r) for r in actual),n+' remaining non-neutral keys: '+repr([r for r in actual if r[1]!=0 and not inside(r)])
 out[n]['after']=actual
 lines.append('%s speech keys preserved %d; total %d; non-neutral outside speech 0; repaired %d'%(n,len(speech),len(actual),len(extras)))
assert set(out)==set(win)
(j/'lip_silence_after.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')
(j/'lip_trim.txt').write_text(chr(10).join(lines),encoding='utf8')
