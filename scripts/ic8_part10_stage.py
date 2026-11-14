import RLPy, os, math
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
T=lambda s:RLPy.RTime.FromValue(int(s*6000))
av={a.GetName():a for a in RLPy.RScene.GetAvatars()}
RLPy.RGlobal.SetTime(T(0))
# Existing camera math; no camera jobs from part 9 are executed.
ns={};exec(open(r'C:\Users\Apinan\Documents\iClone Story Pipeline\scripts\ic8_part9_cams.py',encoding='utf-8').read().split('try:\n')[0],ns)
look=ns['look']
def setpos(o,xyz,q=None):
 c=o.GetControl('Transform');tr=RLPy.RTransform();c.GetValue(T(0),tr)
 tr.T().x,tr.T().y,tr.T().z=xyz
 if q:tr.R().x,tr.R().y,tr.R().z,tr.R().w=q
 c.SetValue(T(0),tr)
def head(a):
 b=next(b for b in a.GetSkeletonComponent().GetSkinBones() if b.GetName().endswith('Head'))
 return b
# Head look at seated Oi.
monk=av['p3_monk'];oi=av['p3_oi']
monk.GetSkeletonComponent().GetLookAtComponent().AddLookAtKey(T(0),T(1),head(oi),1.0,0.0)
for a in (monk,oi):a.GetFaceComponent().SetAutoBlinkName('Normal')
RLPy.RScene.ClearSelectObjects();RLPy.RScene.SelectObject(oi)
RLPy.RFileIO.LoadFile(r'G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น\Digital Soul 100+\1.Watch\Look front.iTalk')
fc=oi.GetFaceComponent();cl=fc.GetClip(fc.GetClipCount()-1);cl.SetSpeed(cl.GetClipLength().ToFloat()/6000/13.84)
# Daylight soft face fill.
for key,xyz,target in [('monk',(-980,220,210),(-860,450,155)),('oi',(-700,450,160),(-860,300,85))]:
 lights=RLPy.RScene.FindObjects(RLPy.EObjectType_Light)
 source=next((l for l in lights if l.GetName()=='Point light'),None)
 if source:
  light=source.Clone();light.SetName('FaceLight_'+key);setpos(light,xyz)
  light.SetColor(T(0),RLPy.RRgb(255,236,214));light.SetMultiplier(T(0),0.04);light.SetRange(T(0),700);light.SetCastShadow(False)
cam=RLPy.RScene.GetCameras()[0]
RLPy.RGlobal.RemoveAllAnimations(cam)
cp=(-530,-250,210);tg=(-850,350,85)
setpos(cam,cp,look(cp,tg));cam.SetFocalLength(T(0),80)
d=RLPy.RCameraDofData();d.SetEnable(False);k=RLPy.RKey();k.SetTime(T(0));cam.AddDofKey(k,d)
RLPy.RScene.SetCurrentCamera(cam);RLPy.RGlobal.SetTime(T(1))
RLPy.RGlobal.RenderImage(os.path.join(J,'p10_stage.png'))
open(os.path.join(J,'p10_stage.txt'),'w').write(str({n:(head(a).WorldTransform().T().x,head(a).WorldTransform().T().y,head(a).WorldTransform().T().z) for n,a in av.items()}))
