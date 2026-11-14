# Part 7: static arm pose only, explicit nod/blink/smile; no motion asset, no video.
import os,math,random,traceback,RLPy
from PySide2 import QtWidgets
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
log=[]
def settle(s):
 RLPy.RGlobal.SetTime(T(s));QtWidgets.QApplication.processEvents();RLPy.RGlobal.ForceViewportUpdate();QtWidgets.QApplication.processEvents()
def pos(b):
 p=b.WorldTransform().T();return [float(p.x),float(p.y),float(p.z)]
try:
 RLPy.RGlobal.Stop();settle(0)
 av={a.GetName():a for a in RLPy.RScene.GetAvatars()}
 if 'Sunee' in av:
  RLPy.RScene.Hide(av['Sunee']);av['Sunee'].SetVisible(T(0),False);av['Sunee'].SetVisible(T(42.1),False);log.append('Sunee visible='+str(av['Sunee'].IsVisible(T(0))))
 pr=av['ปรียา'];sk=pr.GetSkeletonComponent();bones={b.GetName():b for b in sk.GetSkinBones()}
 log.append('Priya existing skeleton clips '+str(sk.GetClipCount()))
 clip=sk.GetClip(0) if sk.GetClipCount() else sk.AddClip(T(0))
 clip.SetLength(T(42.1))
 for side in ('L','R'):
  bone=bones['CC_Base_'+side+'_Upperarm'];hand=bones['CC_Base_'+side+'_Hand']
  db=clip.GetControl('Layer',bone).GetDataBlock()
  ctrls=[db.GetControl('Rotation/Rotation'+x) for x in 'XYZ']
  def rot(axis=None,deg=0):
   for i,c in enumerate(ctrls):
    for t in (0,42.1):c.SetValue(T(t),math.radians(deg) if i==axis else 0.)
   pr.Update();settle(.1);settle(0)
  rot();before=pos(hand)
  log.append('POSE '+side+' restored zero layer; existing natural hand='+str(before))
  if before[2]>110:raise RuntimeError('Existing hand pose too high')
 RLPy.RGlobal.SetProjectLength(T(42.1));RLPy.RGlobal.SetEndTime(T(42.1));RLPy.RGlobal.SetPreviewEndTime(T(42.1))
 for ix,(nm,amp) in enumerate((('นาวี18',.5),('ธีภพ',.45),('ปรียา',.45))):
  fc=av[nm].GetFaceComponent();rnd=random.Random(5+ix*19);start=21.5 if ix<2 else 0.;period=5.6+ix*.7
  fc.SetAutoBlinkName('Normal');fc.BeginKeyEditing();n=0;nb=0;t=start;down=True
  while t<42.1:
   w=amp*rnd.uniform(.85,1.1);fc.AddExpressionKeys(T(t),['Head_Turn_Down','Head_Turn_Up'],[w,0.] if down else [0.,w*.5],T(period/2));n+=1;t+=period/2;down=not down
  fc.AddExpressionKeys(T(42.1),['Head_Turn_Down','Head_Turn_Up'],[amp*.5,0],T(1.5));n+=1
  b=start+rnd.uniform(1,2)
  while b+.16<42.1:
   for dt,w in ((0,0),(.07,1),(.16,0)):fc.AddExpressionKeys(T(b+dt),['Eye_Blink_L','Eye_Blink_R'],[w,w],T(.05));nb+=1
   b+=rnd.uniform(3,5.5)
  fc.AddExpressionKeys(T(42.1),['Eye_Blink_L','Eye_Blink_R'],[0,0],T(.05));nb+=1
  if nm!='นาวี18':
   available=set(sum([list(fc.GetExpressionNames(g)) for g in ('MouthBase','MouthMove','Cheeks','Brows')],[]))
   wanted={'Mouth_Corner_Up_L':.42,'Mouth_Corner_Up_R':.42,'Mouth_Corner_Pull_L':.16,'Mouth_Corner_Pull_R':.16,'Eye_Cheek_Raise_L':.20,'Eye_Cheek_Raise_R':.20}
   names=[k for k in wanted if k in available];weights=[wanted[k]*(1 if ix==1 else .75) for k in names]
   assert names,'No smile channels'
   begin=16.4 if ix==1 else 31.5
   for sec,mul in ((0,0),(begin-.5,0),(begin,1),(37.1,1),(42.1,.85)):
    fc.AddExpressionKeys(T(sec),names,[w*mul for w in weights],T(.5))
   log.append(nm+' smile channels '+str(names))
  fc.EndKeyEditing();log.append('%s appended nod events=%d blink events=%d start=%.1f end=42.1'%(nm,n,nb,start))
 settle(33);log.append('Priya final hands '+str([pos(bones['CC_Base_'+s+'_Hand']) for s in ('L','R')]))
 log.append('end_ticks='+str(RLPy.RGlobal.GetEndTime().ToFloat()));log.append('DONE')
except Exception:log.append('ERROR '+traceback.format_exc())
open(os.path.join(J,'p141_pose.txt'),'w',encoding='utf-8').write('\n'.join(log))
