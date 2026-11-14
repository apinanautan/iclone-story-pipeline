# Part 8 cast: load real Sunee, Look front, visibility, nod/blink/smile, timeline 52.1 s. No save.
import os,random,traceback,RLPy
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')
T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
END=52.1;log=[]
def fl():open(os.path.join(J,'p8_cast.txt'),'w',encoding='utf-8').write('\n'.join(log))
try:
 RLPy.RGlobal.Stop();RLPy.RScene.ClearSelectObjects();RLPy.RGlobal.SetTime(T(0))
 before={a.GetName() for a in RLPy.RScene.GetAvatars()}
 RLPy.RFileIO.LoadFile(r"E:\ไฟล์งาน\ไฟล์ Save\นิทาน\สุนีย์_local.iAvatar")
 new=[a for a in RLPy.RScene.GetAvatars() if a.GetName() not in before];log.append('new avatars '+str([a.GetName() for a in new]));fl()
 su=new[0];c=su.GetControl('Transform');tr=RLPy.RTransform();c.GetValue(T(0),tr)
 tr.T().x,tr.T().y,tr.T().z=-284.7,470.5,0;tr.R().x,tr.R().y,tr.R().z,tr.R().w=0,0,1,0;c.SetValue(T(0),tr)
 RLPy.RScene.ClearSelectObjects();RLPy.RScene.SelectObject(su)
 log.append('lookfront ret '+str(RLPy.RFileIO.LoadFile(r"E:\ไฟล์งาน\ไฟล์ Save\นิทาน\Look_front_local.iTalk")));RLPy.RScene.ClearSelectObjects();fl()
 av={a.GetName():a for a in RLPy.RScene.GetAvatars()};th=av['ธีภพ'];nv=av['นาวี18'];pr=av['ปรียา']
 RLPy.RScene.Hide(pr);pr.SetVisible(T(0),False)
 su.SetVisible(T(0),False);su.SetVisible(T(32.6),True)
 th.SetVisible(T(32.6),False)
 RLPy.RGlobal.SetProjectLength(T(END));RLPy.RGlobal.SetEndTime(T(END));RLPy.RGlobal.SetPreviewEndTime(T(END))
 for ix,(a,amp,start) in enumerate(((su,.45,0.),(nv,.5,42.6))):
  fc=a.GetFaceComponent();rnd=random.Random(81+ix);period=5.8+ix*.6;fc.SetAutoBlinkName('Normal');fc.BeginKeyEditing();t=start;down=True;n=nb=0
  while t<END:
   w=amp*rnd.uniform(.85,1.1);fc.AddExpressionKeys(T(t),['Head_Turn_Down','Head_Turn_Up'],[w,0.] if down else [0.,w*.5],T(period/2));n+=1;t+=period/2;down=not down
  fc.AddExpressionKeys(T(END),['Head_Turn_Down','Head_Turn_Up'],[amp*.5,0],T(1.5))
  b=start+rnd.uniform(1,2)
  while b+.16<END:
   for dt,w in ((0,0),(.07,1),(.16,0)):fc.AddExpressionKeys(T(b+dt),['Eye_Blink_L','Eye_Blink_R'],[w,w],T(.05));nb+=1
   b+=rnd.uniform(3,5.5)
  fc.AddExpressionKeys(T(END),['Eye_Blink_L','Eye_Blink_R'],[0,0],T(.05))
  if a is nv:  # Navee: heart flutters, gentle smile 21.4-33.5
   names=['Mouth_Corner_Up_L','Mouth_Corner_Up_R','Mouth_Corner_Pull_L','Mouth_Corner_Pull_R','Eye_Cheek_Raise_L','Eye_Cheek_Raise_R'];wt=[.35,.35,.13,.13,.17,.17]
   for sec,m in ((20.9,0),(21.4,1),(32.6,1),(34.5,0),(END,0)):fc.AddExpressionKeys(T(sec),names,[x*m for x in wt],T(.5))
  fc.EndKeyEditing();log.append('%s nod %d blink %d'%(a.GetName(),n,nb));fl()
 RLPy.RGlobal.SetTime(T(0));log.append('end '+str(RLPy.RGlobal.GetEndTime().ToFloat()));log.append('DONE')
except Exception:log.append('ERROR '+traceback.format_exc())
fl()
