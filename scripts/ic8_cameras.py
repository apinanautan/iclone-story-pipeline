# Rebuild Part 9 eight single MCU shots. Stills only, never video.
import os,math,time,traceback,RLPy
from PySide2 import QtWidgets
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
NARI='นาวีวัยมัธยม';log=[];NM={'N':NARI,'S':'สุนีย์'}
def flush():open(os.path.join(J,'p9_cams_cams.txt'),'w',encoding='utf-8').write('\n'.join(log))
def settle(s):
 RLPy.RGlobal.SetTime(T(s));QtWidgets.QApplication.processEvents();RLPy.RGlobal.ForceViewportUpdate();QtWidgets.QApplication.processEvents()
def qm(a,b):
 x,y,z,w=a;X,Y,Z,W=b
 return(w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z)
def look(c,t):
 dx,dy,dz=(t[i]-c[i] for i in range(3));yaw=math.atan2(-dx,dy);pit=math.atan2(dz,math.hypot(dx,dy))
 return qm((0,0,math.sin(yaw/2),math.cos(yaw/2)),qm((math.sin(pit/2),0,0,math.cos(pit/2)),(math.sqrt(.5),0,0,math.sqrt(.5))))
SH=[('N',-60,-60,235,232,80,0,5),('S',58,58,225,222,100,5,9.5),('N',-62,-58,215,213,100,9.5,12.5),('S',60,56,230,228,80,12.5,18),('N',-58,-59,225,223,100,18,23.5),('S',59,55,215,213,100,23.5,29),('N',-61,-57,225,223,80,29,34),('S',56,58,235,233,80,34,38.8),('N',-61,-57,215,213,100,38.8,43.1),('S',60,56,235,233,80,43.1,48.1)]
try:
 RLPy.RGlobal.Stop()
 av={a.GetName():a for a in RLPy.RScene.GetAvatars()};cams={c.GetName():c for c in RLPy.RScene.GetCameras()};CS=[cams['Cam41_A'],cams['Cam41_B']]
 for c in CS:RLPy.RGlobal.RemoveAllAnimations(c)
 for ix,(name,a0,a1,r0,r1,fl,s,e) in enumerate(SH):
  cam=CS[ix%2];hb=next(b for b in av[NM[name]].GetSkeletonComponent().GetSkinBones() if b.GetName().endswith('Head'))
  settle(s);p=hb.WorldTransform().T();G0=(float(p.x),float(p.y),float(p.z)+3)
  settle(e);p=hb.WorldTransform().T();G1=(float(p.x),float(p.y),float(p.z)+3)
  times=sorted(set([max(0,s-.5),max(0,s-.25)]+[s+.25*i for i in range(int((e-s)/.25)+1)]+[e,e+.25,e+.5]))
  for t in times:
   u=(t-s)/(e-s);r=r0+(r1-r0)*u;th=math.radians(a0+(a1-a0)*u);G=tuple(G0[k]+(G1[k]-G0[k])*u for k in range(3));sign=-1
   P=(G[0]+sign*r*math.sin(th),G[1]+sign*r*math.cos(th),G[2]);ctl=cam.GetControl('Transform');tr=RLPy.RTransform();ctl.GetValue(T(t),tr);tr.T().x,tr.T().y,tr.T().z=P;tr.R().x,tr.R().y,tr.R().z,tr.R().w=look(P,G);ctl.SetValue(T(t),tr);ctl.SetKeyTransition(T(t),RLPy.ETransitionType_Linear,0.)
   cam.SetFocalLength(T(t),fl);d=RLPy.RCameraDofData();d.SetEnable(True);d.SetFocus(math.dist(P,G));d.SetRange(55);d.SetFarTransitionRegion(100);d.SetNearTransitionRegion(70);d.SetFarBlurScale(1);d.SetNearBlurScale(1);k=RLPy.RKey();k.SetTime(T(t));cam.AddDofKey(k,d)
  log.append('SHOT %d %s %s %.1f-%.1f lens%d radius%d-%d keys%d target%s/%s'%(ix+1,cam.GetName(),name,s,e,fl,r0,r1,len(times),G0,G1));flush()
 RLPy.RScene.ClearSwitchCameraKeys()
 for ix,sh in enumerate(SH):RLPy.RScene.AddSwitchCameraKey(T(sh[6]),CS[ix%2])
 log.append('switch_frames '+str(RLPy.RScene.GetSwitchCameraFrameIndexs(RLPy.RGlobal.GetFps())));flush()
 for ix,sh in enumerate(SH):
  for label,sec in (('a',sh[6]+.02),('b',(sh[6]+sh[7])/2),('c',sh[7]-.02)):
   RLPy.RScene.SetCurrentCamera(CS[ix%2]);settle(sec);time.sleep(.1);RLPy.RGlobal.ForceViewportUpdate();path=os.path.join(J,'p9_cams_%02d_%s.png'%(ix+1,label));RLPy.RGlobal.RenderImage(path)
  log.append('STILLS %d'%(ix+1));flush()
 settle(0);RLPy.RScene.ClearSelectObjects();log.append('DONE');flush()
except Exception:log.append('ERROR '+traceback.format_exc());flush()
