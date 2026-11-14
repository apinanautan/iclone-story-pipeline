import RLPy, os
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
T=lambda s:RLPy.RTime.FromValue(int(s*6000))
lines=[]
for p in RLPy.RScene.GetProps():
    if p.GetName().startswith('p10_'):
        lines.append(p.GetName())
        try:
            lo=RLPy.RVector3(); hi=RLPy.RVector3(); cen=RLPy.RVector3()
            result=p.GetBounds(lo,hi,cen)
            lines.append(str(result)+' bounds '+str([(v.x,v.y,v.z) for v in (lo,hi,cen)]))
        except Exception as e: lines.append(str(e))
a=next(a for a in RLPy.RScene.GetAvatars() if a.GetName()=='p3_oi')
RLPy.RGlobal.RemoveAllAnimations(a)
RLPy.RScene.ClearSelectObjects();RLPy.RScene.SelectObject(a);RLPy.RGlobal.SetTime(T(0))
open(os.path.join(J,'p10_inspect.txt'),'w').write('\n'.join(lines))
