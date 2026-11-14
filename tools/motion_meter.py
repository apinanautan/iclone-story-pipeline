# How busy is the motion in a rendered clip? Mean optical-flow per shot (px/s at 480p), cuts excluded.
# Usage: python -I tools/motion_meter.py <mp4> [shot start times ...]
# User 2026-11-14: folk tales must move slowly (no fidgety "ยุกยิก" motion). Compare before/after a speed change;
# camera moves are slow (<=2 deg) so most of the flow is the actors.
import sys
import cv2
import numpy as np
src = sys.argv[1]
cuts = [float(x) for x in sys.argv[2:]] or [0.0]
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
prev, i, rows = None, 0, []
while True:
    ok, img = cap.read()
    if not ok: break
    g = cv2.cvtColor(cv2.resize(img, (426, 240)), cv2.COLOR_BGR2GRAY)
    if prev is not None:
        f = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag = np.linalg.norm(f, axis=2)
        rows.append((i / fps, float(np.percentile(mag, 95)) * fps * 2))  # 95th pct = moving parts; x2 -> 480p px/s
    prev = g; i += 1
cap.release()
bounds = cuts + [rows[-1][0] + 1]
allv = []
for k in range(len(cuts)):
    a, b = bounds[k] + 0.2, bounds[k + 1] - 0.2
    v = [m for t, m in rows if a <= t <= b]
    if v:
        allv += v
        print('shot %d %5.1f-%5.1f  mean %6.1f px/s  p90 %6.1f' % (k + 1, bounds[k], bounds[k + 1], np.mean(v), np.percentile(v, 90)))
print('ALL mean %.1f px/s  p90 %.1f' % (np.mean(allv), np.percentile(allv, 90)))
