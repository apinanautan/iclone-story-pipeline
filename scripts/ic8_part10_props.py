import os, math, RLPy
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
T=lambda s:RLPy.RTime.FromValue(int(s*6000))
log=[]
for i,path in enumerate([r'C:\Users\Apinan\Downloads\24a971ceded62fadcd4876b7f9827d41.fbx',r'C:\Users\Apinan\Downloads\ca7b1eaf7e0a2411ddd4a41decc40ae5.fbx']):
    before={p.GetID() for p in RLPy.RScene.GetProps()}
    result=RLPy.RFileIO.LoadFile(path)
    new=[p for p in RLPy.RScene.GetProps() if p.GetID() not in before]
    log.append(str((path,str(result),[p.GetName() for p in new])))
    for p in new:
        p.SetName('p10_side_prop_'+str(i))
        ctl=p.GetControl('Transform'); tr=RLPy.RTransform(); ctl.GetValue(T(0),tr)
        tr.T().x=-800+i*40; tr.T().y=290; tr.T().z=0
        ctl.SetValue(T(0),tr)
RLPy.RGlobal.SetTime(T(0))
open(os.path.join(J,'p10_props.txt'),'w',encoding='utf-8').write('\n'.join(log))
