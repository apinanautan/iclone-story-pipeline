# Part 4 monk mouth QA: speaking and silent frames.
# WARNING: this keys Camera_0. Run it BEFORE the cameras script, or re-run scripts/ic8_part4_cams.py afterwards (it did corrupt shot 3 once).
import math, os, traceback
import RLPy
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
def qmul(a,b):
    ax,ay,az,aw=a; bx,by,bz,bw=b
    return (aw*bx+ax*bw+ay*bz-az*by,aw*by-ax*bz+ay*bw+az*bx,aw*bz+ax*by-ay*bx+az*bw,aw*bw-ax*bx-ay*by-az*bz)
log=[]
try:
    a=next(x for x in RLPy.RScene.GetAvatars() if x.GetName()=='p3_monk')
    cam=next(x for x in RLPy.RScene.GetCameras() if x.GetName()=='Camera_0')
    head=next(b for b in a.GetSkeletonComponent().GetSkinBones() if b.GetName().endswith('Head'))
    times=[('speak1',24.5),('speak2',31.8),('silent',22.0)]
    for label,s in times:
        RLPy.RGlobal.SetTime(T(s)); h=head.WorldTransform().T(); hx,hy,hz=h.x,h.y,h.z+8
        c=(hx,hy-90,hz); dx,dy=hx-c[0],hy-c[1]; yaw=math.degrees(math.atan2(-dx,dy))/2
        q=qmul((0,0,math.sin(math.radians(yaw)),math.cos(math.radians(yaw))),(math.sin(math.radians(45)),0,0,math.cos(math.radians(45))))
        ctl=cam.GetControl('Transform'); tr=RLPy.RTransform(); ctl.GetValue(T(s),tr); tr.T().x,tr.T().y,tr.T().z=c; tr.R().x,tr.R().y,tr.R().z,tr.R().w=q; ctl.SetValue(T(s),tr); cam.SetFocalLength(T(s),50)
        RLPy.RScene.SetCurrentCamera(cam); RLPy.RGlobal.RenderImage(os.path.join(J,'mouth4_%s.png'%label)); log.append('%s %.2f'% (label,s))
    RLPy.RGlobal.SetTime(T(0))
except Exception: log.append(traceback.format_exc())
open(os.path.join(J,'mouth4_log.txt'),'w').write('\n'.join(log))
