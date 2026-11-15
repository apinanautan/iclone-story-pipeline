"""In-memory rental spot survey. Existing scene/Camera only; never load/save."""
import os, math, json, traceback
import RLPy
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
O=os.path.join(J,'spots'); NAME='หน้าห้องเช่าเมียน้อย'
T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
def qm(a,b):
 ax,ay,az,aw=a;bx,by,bz,bw=b
 return(aw*bx+ax*bw+ay*bz-az*by,aw*by-ax*bz+ay*bw+az*bx,aw*bz+ax*by-ay*bx+az*bw,aw*bw-ax*bx-ay*by-az*bz)
def look(c,t):
 dx,dy,dz=[t[i]-c[i] for i in range(3)]; y=math.atan2(-dx,dy);p=math.atan2(dz,math.hypot(dx,dy))
 return qm((0,0,math.sin(y/2),math.cos(y/2)),qm((math.sin(p/2),0,0,math.cos(p/2)),(math.sin(math.pi/4),0,0,math.cos(math.pi/4))))
def setc(cam,c,t,f):
 ctl=cam.GetControl('Transform');tr=RLPy.RTransform();ctl.GetValue(T(0),tr);tr.T().x,tr.T().y,tr.T().z=c
 q=look(c,t);tr.R().x,tr.R().y,tr.R().z,tr.R().w=q;ctl.SetValue(T(0),tr);cam.SetFocalLength(T(0),f)
 RLPy.RGlobal.SetTime(T(0))
def vec(v):return [v.x,v.y,v.z]
log=[];hidden=[];roof=None
try:
 RLPy.RGlobal.Stop();RLPy.RGlobal.SetTime(T(0))
 cam=RLPy.RScene.FindObject(RLPy.EObjectType_Camera,'Camera')
 assert cam is not None,'Existing Camera missing; abort'
 RLPy.RScene.SetCurrentCamera(cam)
 d=RLPy.RCameraDofData();d.SetEnable(False);k=RLPy.RKey();k.SetTime(T(0));cam.AddDofKey(k,d)
 log.append('CAM_METHODS '+str([n for n in dir(cam) if any(x in n.lower() for x in ['fov','angle','aperture','film','focal'])]))
 for p in RLPy.RScene.GetProps():
  if p.GetName()=='node_0':
   log.append('ROOT METHODS '+str([n for n in dir(p) if any(x in n.lower() for x in ['child','mesh','visible','bound'])]))
   try:log.append('CHILDREN '+str([(x.GetName(),str(type(x))) for x in p.GetChildren()]))
   except Exception as e:log.append(str(e))
 hidden=[]
 for name in ['RootNode_5','RootNode_8','coconut palm']:
  p=RLPy.RScene.FindObject(RLPy.EObjectType_Prop,name)
  if p is not None:hidden.append((p,p.IsVisible(T(0))));p.SetVisible(T(0),False);RLPy.RScene.Hide(p)
 views=[('1',[-4100,-3900,600],[-4100,-2450,100],10),('2',[-5550,-2450,600],[-4100,-2450,100],10),('3',[-4100,-1000,600],[-4100,-2450,100],10),('4',[-2650,-2450,600],[-4100,-2450,100],10),('5',[-5070,-3530,600],[-4100,-2450,100],10),('6',[-4100,-2450,3500],[-4100,-2450,80],24)]
 meta=[]
 for i,c,t,f in views:
  roof=None
  if i=='6':
   # Building is one merged mesh/material: no independent roof object exists.
   # Hide its complete shell only for the overhead, then restore immediately.
   roof=RLPy.RScene.FindObject(RLPy.EObjectType_Prop,'node_0');roofvis=roof.IsVisible(T(0));roof.SetVisible(T(0),False)
   log.append('OVERHEAD: merged node_0 shell hidden (roof cannot be isolated)')
  setc(cam,c,t,f)
  row={'id':i,'pos':c,'target':t,'focal':f,'quaternion':list(look(c,t))}
  for method in ['GetAngleOfView','GetFov','GetFOV','GetAperture','GetFocalLength']:
   if hasattr(cam,method):
    for args in [(T(0),),()]:
     try: row[method]=str(getattr(cam,method)(*args));break
     except Exception:pass
  path=os.path.join(O,NAME+'_wide_'+i+'.png');r=RLPy.RGlobal.RenderImage(path);row['file']=path;meta.append(row)
  with open(os.path.join(O,'rental_wide_meta.json'),'w',encoding='utf-8') as h:json.dump(meta,h,ensure_ascii=False,indent=2)
  if roof is not None:roof.SetVisible(T(0),roofvis)
  log.append('RENDER '+i+' '+str(r))
except Exception:log.append(traceback.format_exc())
finally:
 if roof is not None:roof.SetVisible(T(0),roofvis)
 for p,v in hidden:
  RLPy.RScene.Show(p);p.SetVisible(T(0),v)
  log.append('RESTORED '+p.GetName()+' '+str(p.IsVisible(T(0))))
with open(os.path.join(O,'rental_wide_log.txt'),'w',encoding='utf-8') as h:h.write('\n'.join(log))
