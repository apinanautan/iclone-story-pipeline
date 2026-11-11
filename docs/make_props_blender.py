import bpy, bmesh, math, os, random
random.seed(7)
OUT = r"E:\ไฟล์งาน\ไฟล์ Save\นิทาน\prop_4"
os.makedirs(OUT, exist_ok=True)

def clear():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
    for b in list(bpy.data.meshes): bpy.data.meshes.remove(b)
    for m in list(bpy.data.materials): bpy.data.materials.remove(m)

def mat(name, rgb, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

def assign(o, m):
    o.data.materials.clear(); o.data.materials.append(m)

def shade_smooth(o):
    for p in o.data.polygons: p.use_smooth = True

def lathe(name, pts, steps=48):
    """pts: list of (r,z) profile, revolve around Z."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    rings = []
    for (r, z) in pts:
        ring = []
        for i in range(steps):
            a = 2 * math.pi * i / steps
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        for i in range(steps):
            j = (i + 1) % steps
            try: bm.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]))
            except ValueError: pass
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    shade_smooth(o); return o

def export(objs, fname):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, fname), use_selection=True, global_scale=100.0,
        apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', axis_forward='-Y', axis_up='Z',
        object_types={'MESH'}, mesh_smooth_type='FACE', add_leaf_bones=False)

# ---------- 1) mixing bowl with flour (units: metres) ----------
clear()
R, H, T = 0.125, 0.11, 0.004
prof = [(0.07, 0.0), (0.09, 0.004), (0.115, 0.04), (R, 0.085), (R + 0.004, H), (R - 0.001, H + 0.003),
        (R - T - 0.001, H), (R - T - 0.004, 0.085), (R - T - 0.026, 0.04), (0.085 - T, 0.012), (0.0, 0.010)]
bowl = lathe("MixingBowl", prof); assign(bowl, mat("Enamel", (0.86, 0.88, 0.9), 0.35, 0.1))
# flour mound inside
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0.012), segments=40, ring_count=20)
fl = bpy.context.active_object; fl.name = "FlourMound"; fl.scale = (0.075, 0.075, 0.032)
bpy.ops.object.transform_apply(scale=True)
# lumpy surface
bm = bmesh.new(); bm.from_mesh(fl.data)
for v in bm.verts:
    if v.co.z > 0: v.co.z += random.uniform(-0.002, 0.003)
bm.to_mesh(fl.data); bm.free(); shade_smooth(fl); assign(fl, mat("Flour", (0.96, 0.95, 0.9), 0.95))
# a small dough ball resting on the flour
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(0.012, -0.008, 0.05), segments=32, ring_count=16)
dg = bpy.context.active_object; dg.name = "Dough"; dg.scale = (1, 1, 0.8); shade_smooth(dg); assign(dg, mat("Dough", (0.93, 0.87, 0.74), 0.9))
export([bowl, fl, dg], "ถ้วยผสมแป้ง.fbx")

# ---------- 2) cutting board with flour + rolling pin ----------
clear()
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.0125)); board = bpy.context.active_object
board.name = "CuttingBoard"; board.scale = (0.40, 0.28, 0.025); bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.modifier_add(type='BEVEL'); board.modifiers["Bevel"].width = 0.004; board.modifiers["Bevel"].segments = 2
bpy.ops.object.modifier_apply(modifier="Bevel"); assign(board, mat("Wood", (0.55, 0.36, 0.2), 0.55))
# flour patch (flattened sphere) + dusting blobs
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(-0.03, 0.0, 0.026), segments=40, ring_count=16)
fp = bpy.context.active_object; fp.name = "FlourPatch"; fp.scale = (0.14, 0.10, 0.006); bpy.ops.object.transform_apply(scale=True)
shade_smooth(fp); assign(fp, mat("Flour", (0.96, 0.95, 0.9), 0.95))
blobs = [fp]
for i in range(9):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(random.uniform(-0.17, 0.12), random.uniform(-0.11, 0.11), 0.0255), segments=16, ring_count=8)
    b = bpy.context.active_object; s = random.uniform(0.012, 0.03); b.scale = (s, s * random.uniform(0.7, 1.2), 0.003)
    bpy.ops.object.transform_apply(scale=True); assign(b, fp.data.materials[0]); blobs.append(b)
# dough ball on the flour
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(-0.05, 0.01, 0.062), segments=32, ring_count=16)
dg = bpy.context.active_object; dg.name = "Dough"; dg.scale = (1.1, 1.0, 0.75); shade_smooth(dg); assign(dg, mat("Dough", (0.93, 0.87, 0.74), 0.9))
# rolling pin lying on the board edge (axis along X), with two handles
bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.26, location=(0.07, -0.19 + 0.0, 0.052), vertices=32)
rp = bpy.context.active_object; rp.name = "RollingPin"; rp.rotation_euler = (0, math.pi / 2, 0); rp.location = (0.0, -0.1, 0.048)
bpy.ops.object.transform_apply(rotation=True); shade_smooth(rp); assign(rp, mat("PinWood", (0.72, 0.52, 0.32), 0.5))
hs = []
for sx in (-1, 1):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.07, location=(sx * 0.165, -0.1, 0.048), vertices=24)
    h = bpy.context.active_object; h.rotation_euler = (0, math.pi / 2, 0); bpy.ops.object.transform_apply(rotation=True)
    shade_smooth(h); assign(h, rp.data.materials[0]); hs.append(h)
export([board, fp] + blobs[1:] + [dg, rp] + hs, "เขียงแป้งไม้นวด.fbx")
print("DONE", os.listdir(OUT))
