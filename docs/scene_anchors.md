# Scene anchors (where things go), recorded from the user's marker props

## มหาอกหัก (นิทาน)
### วัด(ยังไม่มีร้านกาแฟ)150
- Front of the temple steps: character at (-860, 450, z 0) yaw 0, temple behind on +Y.
- Gable establishing shot: cam (-1900,-1090,93)→(-1860,-1095,96), target (-790,1500,920-950), 80mm, no DOF.
- Thatched pavilion with mat (model_1): x 1428-3285, y 132-2029 (not used yet).

### ภายในโบสถ์ของวัดอีกวัด
- Floor z ≈ 25765. Altar toward +Y.
- Marker `Box_001` = centre of the villagers' seating circle: (33, 566), floor z = 25774 (box base). Monk sits 4 m toward the altar: (33, 966) yaw 0.
- ! Camera_0 at (93,-184,25974) looking +Y renders only grey blur, no characters. Something blocks it. Ask the user to drop a marker box at the camera position too, or frame the viewport themselves.

- Part 2 tested monk chest-up framing: camera `Camera` at (33,696,25910), target (33,896,25844), **100mm + DOF**. PNG previews at 9s and 60s: head and upper chest in frame, lower robes out of frame. Use for monk shots (7-13.45s, 53.82-75.5s); switching keys not yet built.
