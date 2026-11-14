import RLPy, os
T=lambda s:RLPy.RTime.FromValue(int(s*6000))
lines=[]
for p in RLPy.RScene.GetProps():
    if not p.GetName().startswith('p10_side_prop_'):continue
    a=RLPy.RVector3(); b=RLPy.RVector3(); c=RLPy.RVector3(); p.GetBounds(a,b,c)
    # GetBounds returns max, center, min in this build. Scale by actual height.
    height=max(a.z,b.z,c.z)-min(a.z,b.z,c.z)
    assert height>0
    factor=32.0/height
    ctl=p.GetControl('Transform'); tr=RLPy.RTransform();ctl.GetValue(T(0),tr)
    tr.S().x*=factor;tr.S().y*=factor;tr.S().z*=factor
    ctl.SetValue(T(0),tr)
    lines.append(p.GetName()+' original height '+str(height)+' target 32 cm')
open(os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs','p10_scale.txt'),'w').write('\n'.join(lines))
