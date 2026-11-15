"""Offline conservative capsule-vs-prop-AABB audit of watcher 60fps pose data.
Not triangle-mesh collision certification. No scene or project modifications.
"""
import os,json,math
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
RAD={'Pelvis':16,'Head':12,'L_Hand':7,'R_Hand':7,'L_Foot':9,'R_Foot':9,'L_Forearm':6,'R_Forearm':6,'L_Upperarm':7,'R_Upperarm':7,'L_Calf':7,'R_Calf':7,'L_Thigh':9,'R_Thigh':9}
LINKS=[('Pelvis','Head',16)]+[(side+a,side+b,r) for side in ['L_','R_'] for a,b,r in [('Upperarm','Forearm',7),('Forearm','Hand',6),('Thigh','Calf',9),('Calf','Foot',7)]]
def pointbox(p,mn,mx):return math.sqrt(sum(max(mn[i]-p[i],0,p[i]-mx[i])**2 for i in range(3)))
def segmentbox(a,b,mn,mx):
 def f(t):return pointbox([a[i]+t*(b[i]-a[i]) for i in range(3)],mn,mx)
 lo,hi=0.,1.
 for _ in range(20):
  u,v=(2*lo+hi)/3,(lo+2*hi)/3
  if f(u)<f(v):hi=v
  else:lo=u
 return min(f(0),f(1),f((lo+hi)/2))
def audit(label):
 d=json.load(open(os.path.join(J,'g2_'+label+'_poses.json'),encoding='utf8'))
 assert d.get('done'),d.get('error')
 out={'label':label,'sample_count':len(d['samples']),'max_jump':d['max_jump'],'collision':[],'face':{}}
 for p in d['props']:
  if p['name']=='Floor_001':continue
  if p['visible'] is False:out['collision'].append({'prop':p['name'],'excluded':'visibility false'});continue
  for actor in ['N','K']:
   best=(1e9,None,None);hits=[];mn,mx=p['min'],p['max']
   for s in d['samples']:
    pose=s['pose'][actor]
    values=[(pointbox(v,mn,mx)-RAD.get(b,5),b) for b,v in pose.items()]
    values += [(segmentbox(pose[a],pose[b],mn,mx)-r,a+'--'+b) for a,b,r in LINKS if a in pose and b in pose]
    clearance,bone=min(values)
    if clearance<best[0]:best=(clearance,s['t'],bone)
    if clearance<0:hits.append(s['t'])
   out['collision'].append({'prop':p['name'],'actor':actor,'min_clearance_cm':round(best[0],3),'at':best[1],'bone':best[2],'candidate_frames':len(hits),'first':hits[:5],'last':hits[-5:]})
 for k in ['N','K']:
  if 'face' in d['samples'][0]:
   peaks=[]
   for a,z in zip(d['samples'],d['samples'][1:]):
    wa,wz=a['face'][k],z['face'][k]
    keys=wa.keys() if isinstance(wa,dict) else range(len(wa))
    ds=[(abs(float(wz[i])-float(wa[i])),str(i)) for i in keys]
    val,key=max(ds) if ds else (0,'none');peaks.append((val,z['t'],key))
   out['face'][k]={'max_weight_delta_per_frame':max(peaks),'at_42_4':[p for p in peaks if 42.37<=p[1]<=42.44]}
 for actor in ['N','K']:
  out.setdefault('foot_mid_xy_extent_cm',{})[actor]=[max((s['pose'][actor]['L_Foot'][i]+s['pose'][actor]['R_Foot'][i])/2 for s in d['samples'])-min((s['pose'][actor]['L_Foot'][i]+s['pose'][actor]['R_Foot'][i])/2 for s in d['samples']) for i in range(2)]
 open(os.path.join(J,'g2_'+label+'_qa.json'),'w',encoding='utf8').write(json.dumps(out,ensure_ascii=False,indent=2))
 print(label,'frames',len(d['samples']))
 for k,r in d['max_jump'].items():print(k,{b:round(v['max_cm_per_frame'],3) for b,v in r.items() if b in ['Pelvis','L_Hand','R_Hand','L_Foot','R_Foot']})
 for row in out['collision']:print(row)
 print('face',out['face']);print('foot envelope',out['foot_mid_xy_extent_cm'])
 return out
if __name__=='__main__':
 import sys
 for label in sys.argv[1:] or ['before','after']:audit(label)
