import os,json,RLPy
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs'); T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
a=next(x for x in RLPy.RScene.GetAvatars() if x.GetName()=='p3_monk'); v=a.GetVisemeComponent(); c=v.GetClip(0)
out={'count':v.GetClipCount(),'len':c.GetClipLength().ToFloat()/6000,'startOffset':c.GetStartOffset().ToFloat()/6000,'speed':c.GetSpeed()}
for sec in (0,21.9,23.267,35.807,41.15):
 try:out['scene_from_clip_'+str(sec)]=c.ClipTimeToSceneTime(T(sec)).ToFloat()/6000
 except Exception as e:out['scene_from_clip_'+str(sec)+'_error']=repr(e)
 try:out['clip_from_scene_'+str(sec)]=c.SceneTimeToClipTime(T(sec)).ToFloat()/6000
 except Exception as e:out['clip_from_scene_'+str(sec)+'_error']=repr(e)
open(os.path.join(J,'audio_clip_probe3.json'),'w').write(json.dumps(out,indent=2))
