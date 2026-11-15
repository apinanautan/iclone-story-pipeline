import os,json,RLPy
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
a=next(x for x in RLPy.RScene.GetAvatars() if x.GetName()=='p3_monk'); v=a.GetVisemeComponent(); out={'viseme':{}}
for i in range(v.GetClipCount()):
 c=v.GetClip(i); r={'index':i,'dir':[m for m in dir(c) if 'time' in m.lower() or 'clip' in m.lower() or 'offset' in m.lower() or 'length' in m.lower() or 'speed' in m.lower() or 'key' in m.lower()]}
 for m in ('GetClipLength','GetLength','GetLastKeyTime','GetStartOffset','GetSpeed','GetTransitionRange'):
  try:r[m]=getattr(c,m)().ToFloat()/6000.0
  except Exception as e:
   try:r[m]=getattr(c,m)()
   except Exception as e2:r[m+'Error']=str(e2)
 out['viseme'][i]=r
open(os.path.join(J,'audio_clip_probe2.json'),'w').write(json.dumps(out,indent=2))
