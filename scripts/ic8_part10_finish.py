import RLPy, os, math
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
ns={};exec(open(r'C:\Users\Apinan\Documents\iClone Story Pipeline\scripts\ic8_part9_cams.py',encoding='utf-8').read().split('try:\n')[0],ns)
look=ns['look'];END=13.84
av={a.GetName():a for a in RLPy.RScene.GetAvatars()}
oi=av['p3_oi'];monk=av['p3_monk']
def bone(a):return next(b for b in a.GetSkeletonComponent().GetSkinBones() if b.GetName().endswith('Head'))
for a,b in [(oi,monk),(monk,oi)]:a.GetSkeletonComponent().GetLookAtComponent().AddLookAtKey(T(0),T(1),bone(b),1.0,0.0)
fc=oi.GetFaceComponent();fc.BeginKeyEditing()
for s in (0,END):fc.AddExpressionKeys(T(s),['Mouth_Corner_Up','Eye_Cheek_Raise'],[0.25,0.12],T(0.3))
fc.EndKeyEditing()
RLPy.RGlobal.SetTime(T(1))
h=bone(oi).WorldTransform().T();oh=(h.x,h.y,h.z)
h=bone(monk).WorldTransform().T();mh=(h.x,h.y,h.z)
# Two shots only: Oi reaction then monk chest-up. Tail holds second shot.
shots=[(0,5.64,(-1080,620,oh[2]-12),(-1070,605,oh[2]-12),oh,100,65),(5.64,END,(-1100,80,mh[2]-20),(-1090,95,mh[2]-20),mh,100,50)]
cams=list(RLPy.RScene.GetCameras())
assert cams
if len(cams)<2: shots=[(0,END,(-1220,-100,170),(-1210,-85,168),(-860,360,115),80,250)]
for c in cams:RLPy.RGlobal.RemoveAllAnimations(c)
RLPy.RScene.ClearSwitchCameraKeys()
for i,(start,end,c0,c1,target,focal,rng) in enumerate(shots):
 cam=cams[i%len(cams)];RLPy.RScene.AddSwitchCameraKey(T(start),cam)
 n=max(2,math.ceil((end-start)/0.25))
 for k in range(-2,n+3):
  s=start+(end-start-1/60)*k/n
  if not 0<=s<=END:continue
  u=k/n;cp=tuple(c0[j]+(c1[j]-c0[j])*u*0.5 for j in range(3))
  ctl=cam.GetControl('Transform');tr=RLPy.RTransform();ctl.GetValue(T(s),tr)
  tr.T().x,tr.T().y,tr.T().z=cp;tr.R().x,tr.R().y,tr.R().z,tr.R().w=look(cp,target);ctl.SetValue(T(s),tr)
  cam.SetFocalLength(T(s),focal)
  d=RLPy.RCameraDofData();d.SetEnable(True);d.SetFocus(math.dist(cp,target));d.SetRange(rng);d.SetFarTransitionRegion(120);d.SetNearTransitionRegion(60);d.SetFarBlurScale(1);d.SetNearBlurScale(1)
  key=RLPy.RKey();key.SetTime(T(s));cam.AddDofKey(key,d)
 RLPy.RScene.SetCurrentCamera(cam);RLPy.RGlobal.SetTime(T((start+end)/2));RLPy.RGlobal.RenderImage(os.path.join(J,'c10_%02d.png'%i))
RLPy.RGlobal.SetTime(T(0));RLPy.RScene.SetCurrentCamera(cams[0])
open(os.path.join(J,'p10_finish.txt'),'w').write(str((oh,mh,len(shots))))
