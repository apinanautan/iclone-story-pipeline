import bpy, mathutils, math, os
sc=bpy.context.scene; out=os.environ['OUT']
if 'Cube' in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects['Cube'])
rig=[o for o in sc.objects if o.type=='ARMATURE'][0]; r=rig
while r.parent: r=r.parent
pass
sc.render.engine='BLENDER_WORKBENCH'; sc.render.resolution_x=480; sc.render.resolution_y=480
sc.frame_start=1; sc.frame_end=int(os.environ.get("LAST","151"))
cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam); sc.camera=cam
sc.frame_set(1); bpy.context.view_layer.update()
hip=r.matrix_world@rig.pose.bones['Hips'].head if r==rig else (rig.matrix_world@rig.pose.bones['Hips'].head)
hip=rig.matrix_world@rig.pose.bones['Hips'].head
tgt=mathutils.Vector((hip.x,hip.y,max(hip.z,0.5)))
cam.location=tgt+mathutils.Vector((3.0,-3.0,0.6)); cam.rotation_euler=(tgt-cam.location).to_track_quat('-Z','Y').to_euler()
sc.render.image_settings.media_type='VIDEO'; sc.render.image_settings.file_format='FFMPEG'; sc.render.ffmpeg.format='MPEG4'; sc.render.ffmpeg.codec='H264'
sc.render.filepath=out; bpy.ops.render.render(animation=True)
