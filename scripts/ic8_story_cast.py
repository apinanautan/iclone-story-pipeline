import os, math, traceback, RLPy
J = os.path.join(os.environ['LOCALAPPDATA'], 'Tidmunz Studio', 'snapgen_data', 'ic8_jobs')
CH = r'G:\ไดรฟ์ของฉัน\ดวงเมียน้อย\ดวงเมียน้อย ตัวละคร'
MO = r'G:\ไดรฟ์ของฉัน\.ไฟล์ต่างๆ (ห้ามลบ)\โมชั่น'
CAST = {  # file, name, pos (x,y,z), yaw
 'sunee': ('1.สุนีย์ + ปรีชา\\สุนีย์.iAvatar', 'สุนีย์', (-4200, -3180, 85), 133.4),
 'navee': ('2.นารี\\นาวีวัยประถม.iAvatar', 'นาวีวัยประถม', (-4000, -3180, 85), 270),
 'niwat': ('3.นิวัตน์\\นิวัตน์วัยป2.iAvatar', 'นิวัตน์ป2', (-4065, -3160, 85), 261.6),
}
ONLY = None
log = []
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
try:
    log.append('cams=%d' % len(RLPy.RScene.GetCameras()))
    log.append('existing avatars: ' + ', '.join(a.GetName() for a in RLPy.RScene.GetAvatars()))
    for k, (f, nm, pos, yaw) in CAST.items():
        if ONLY and ONLY != k: continue
        if any(a.GetName() == nm for a in RLPy.RScene.GetAvatars()): continue
        before = set(a.GetID() for a in RLPy.RScene.GetAvatars())
        RLPy.RScene.ClearSelectObjects()
        RLPy.RFileIO.LoadFile(os.path.join(CH, f))
        av = [a for a in RLPy.RScene.GetAvatars() if a.GetID() not in before][0]
        av.SetName(nm)
        c = av.GetControl('Transform'); t = RLPy.RTransform(); c.GetValue(T(0), t)
        t.T().x, t.T().y, t.T().z = pos
        h = math.radians(yaw) / 2
        t.R().x, t.R().y, t.R().z, t.R().w = 0, 0, math.sin(h), math.cos(h)
        c.SetValue(T(0), t)
        log.append('%s placed %s' % (nm, pos))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, 'p1_cast_log.txt'), 'w', encoding='utf-8').write('\n'.join(log))
