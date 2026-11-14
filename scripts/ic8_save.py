# Only save Part 8 after still review. No video.
import os,traceback,RLPy
from PySide2 import QtWidgets
J=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs');T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
log=[]
try:
 RLPy.RGlobal.Stop();RLPy.RScene.ClearSelectObjects();RLPy.RGlobal.SetTime(RLPy.RTime.FromValue(0))
 log.append('end_ticks='+str(RLPy.RGlobal.GetEndTime().ToFloat()))
 log.append('preview_end_ticks='+str(RLPy.RGlobal.GetPreviewEndTime().ToFloat()))
 log.append('switches='+str([(p[0].GetName(),p[1]) for p in RLPy.RScene.GetSwitchCameraFrameIndexs(RLPy.RGlobal.GetFps())]))
 for a in RLPy.RScene.GetAvatars():
  if a.GetName()=='Sunee':log.append('Sunee visible='+str(a.IsVisible(T(0))));continue
  fc=a.GetFaceComponent();log.append(a.GetName()+' skeleton_clips='+str(a.GetSkeletonComponent().GetClipCount())+' viseme_clips='+str(a.GetVisemeComponent().GetClipCount()))
  for sec in (0,):
   RLPy.RGlobal.SetTime(T(sec));QtWidgets.QApplication.processEvents();RLPy.RGlobal.ForceViewportUpdate()
   try:log.append(a.GetName()+' expression '+str(sec)+' '+str(fc.GetExpressionWeights(T(sec))))
   except Exception as ex:log.append('expression read '+str(ex))
 for c in RLPy.RScene.GetCameras():
  if c.GetName() in ('Cam41_A','Cam41_B'):log.append(c.GetName()+' transform keys='+str(c.GetControl('Transform').GetKeyCount()))
 RLPy.RGlobal.SetTime(T(0));QtWidgets.QApplication.processEvents();RLPy.RGlobal.ForceViewportUpdate()
 out=r'E:\ไฟล์งาน\ไฟล์ Save\นิทาน\9.iProject'
 log.append('SAVE_START');open(os.path.join(J,'p9_save3.txt'),'w',encoding='utf-8').write('\n'.join(log))
 status=RLPy.RFileIO.SaveProject(out)
 log.append('save_status='+str(status));log.append('bytes='+str(os.path.getsize(out)));log.append('DONE')
except Exception:log.append('ERROR '+traceback.format_exc())
open(os.path.join(J,'p9_save3.txt'),'w',encoding='utf-8').write('\n'.join(log))
