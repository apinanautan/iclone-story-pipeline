"""Temporary survey of marked points; restore reference avatar; never load/save."""
import os,json,math,traceback,RLPy
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs');O=os.path.join(J,'spots');T=lambda s:RLPy.RTime.FromValue(int(s*6000))
def qm(a,b):
 x,y,z,w=a;X,Y,Z,W=b;return(w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z)
def look(c,t):
 dx,dy,dz=[t[i]-c[i] for i in range(3)];y=math.atan2(-dx,dy);p=math.atan2(dz,math.hypot(dx,dy));return qm((0,0,math.sin(y/2),math.cos(y/2)),qm((math.sin(p/2),0,0,math.cos(p/2)),(math.sqrt(.5),0,0,math.sqrt(.5))))
log=[];original=None;ctl=None;rows=[]
try:
 RLPy.RGlobal.Stop();RLPy.RGlobal.SetTime(T(0));cam=RLPy.RScene.FindObject(RLPy.EObjectType_Camera,'Camera');assert cam is not None
 av=next(a for a in RLPy.RScene.GetAvatars() if a.GetName()=='Sunee');ctl=av.GetControl('Transform');original=RLPy.RTransform();ctl.GetValue(T(0),original)
 RLPy.RScene.SetCurrentCamera(cam)
 for p in json.load(open(os.path.join(O,'rental_points.json'),encoding='utf-8')):
  tr=RLPy.RTransform();ctl.GetValue(T(0),tr);tr.T().x,tr.T().y,tr.T().z=p['pos'][0],p['pos'][1],p['pos'][2]+5
  a=math.radians(p['yaw'])/2;tr.R().x,tr.R().y,tr.R().z,tr.R().w=0,0,math.sin(a),math.cos(a);ctl.SetValue(T(0),tr)
  cc=cam.GetControl('Transform');ct=RLPy.RTransform();cc.GetValue(T(0),ct);ct.T().x,ct.T().y,ct.T().z=p['camera'];ct.R().x,ct.R().y,ct.R().z,ct.R().w=look(p['camera'],p['target']);cc.SetValue(T(0),ct);cam.SetFocalLength(T(0),p['focal'])
  d=RLPy.RCameraDofData();d.SetEnable(True);d.SetFocus(math.dist(p['camera'],p['target']));d.SetRange(100);d.SetFarTransitionRegion(150);d.SetNearTransitionRegion(80);d.SetFarBlurScale(1);d.SetNearBlurScale(1);k=RLPy.RKey();k.SetTime(T(0));cam.AddDofKey(k,d)
  RLPy.RGlobal.SetTime(T(0));path=os.path.join(O,'หน้าห้องเช่าเมียน้อย_'+p['id']+'_MCU.png');r=RLPy.RGlobal.RenderImage(path)
  log.append(p['id']+' '+str(r));rows.append(dict(p,file=path,fov=str(cam.GetAngleOfView(T(0)))))
except Exception:log.append(traceback.format_exc())
finally:
 if original is not None:ctl.SetValue(T(0),original);RLPy.RGlobal.SetTime(T(0));log.append('REFERENCE AVATAR RESTORED')
 json.dump(rows,open(os.path.join(O,'rental_mcu_meta.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=2)
 open(os.path.join(O,'rental_mcu_log.txt'),'w',encoding='utf-8').write('\n'.join(log))
