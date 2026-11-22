import RLPy,os,json
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
T=lambda s:RLPy.RTime.FromValue(int(s*6000))
out={}
for a in RLPy.RScene.GetAvatars():
    n=a.GetName()
    if 'Kevin' in n: continue
    pts=[]
    for k in range(0,153):
        RLPy.RGlobal.SetTime(T(k*0.5))
        mx,c,mn=RLPy.RVector3(),RLPy.RVector3(),RLPy.RVector3(); a.GetBounds(mx,c,mn); pts.append((round(c.x),round(c.y)))
    jumps=[(k*0.5,round(((pts[k][0]-pts[k-1][0])**2+(pts[k][1]-pts[k-1][1])**2)**0.5)) for k in range(1,len(pts))]
    out[n]={'range':[max(p[0] for p in pts)-min(p[0] for p in pts),max(p[1] for p in pts)-min(p[1] for p in pts)],'big':[j for j in jumps if j[1]>15]}
open(os.path.join(J,'drift.json'),'w',encoding='utf-8').write(json.dumps(out,ensure_ascii=False))
