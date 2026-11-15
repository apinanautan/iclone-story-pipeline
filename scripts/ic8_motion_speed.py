import os,math,time,traceback,RLPy
from PySide2 import QtWidgets
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
S0,DUR=0.0,31.1
TARGET=4.0   # cm/s mean speed of head+both hands that counts as "slow"
log=[]
def flush():open(os.path.join(J,'p67_a_20261112.txt'),'w',encoding='utf-8').write('\n'.join(log))
def settle(sec):
 RLPy.RGlobal.SetTime(T(sec));QtWidgets.QApplication.processEvents();RLPy.RGlobal.ForceViewportUpdate();QtWidgets.QApplication.processEvents()
def pts(a):
 o=[]
 for b in a.GetSkeletonComponent().GetSkinBones():
  n=b.GetName()
  if n.endswith('Head') or n.endswith('L_Hand') or n.endswith('R_Hand') or n.endswith('LHand') or n.endswith('RHand'):
   p=b.WorldTransform().T();o.append((n,float(p.x),float(p.y),float(p.z)))
 return o
def mean_speed(av,cl,dt=0.25):
 # clip speed is 1.0 here; sample raw clip time t, avatar timeline == clip time
 prev=None;tot=0;cnt=0
 t=S0
 L=cl
 while t<=L:
  settle(t);cur=pts(av)
  if prev is not None and len(cur)==len(prev):
   for (n,x,y,z),(m,x0,y0,z0) in zip(cur,prev):
    tot+=math.dist((x,y,z),(x0,y0,z0))/dt;cnt+=1
  prev=cur;t+=dt
 return tot/max(cnt,1),len(prev or [])
try:
 RLPy.RGlobal.Stop()
 av={a.GetName():a for a in RLPy.RScene.GetAvatars()}
 for nm in ('นาวีวัยมัธยม','วินัยวัยมัธยม'):
  a=av[nm];sk=a.GetSkeletonComponent();cl=sk.GetClip(0)
  raw=cl.GetClipLength();Lraw=(raw.ToFloat() if hasattr(raw,'ToFloat') else raw.GetValue());Lraw=Lraw/6000.0 if Lraw>1000 else Lraw
  cl.SetSpeed(1.0)
  m,n=mean_speed(a,Lraw)
  s=max(0.15,min(0.30,TARGET/m)) if m>0 else 0.2
  cl.SetSpeed(s)
  log.append('%s raw clip %.1fs: mean head+hands speed at 100%% = %.2f cm/s (%d pts) -> chosen speed %.3f (target %.1f cm/s); clip covers %.1f s of raw in %.1f s'%(nm,Lraw,m,n,s,TARGET,DUR*s,DUR));flush()
 settle(1.0);log.append('DONE')
except Exception:log.append('ERROR '+traceback.format_exc())
flush()
