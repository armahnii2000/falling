import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUTPUT_DIR = "/Users/georgearmah/into-the-darkness/assets/ui"
os.makedirs(f"{OUTPUT_DIR}/blocks", exist_ok=True)

# 1. Blender script to render the 3D Titan Monolith with brushed titanium beveled edges and obsidian glass face
blender_script = """
import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
scene.render.resolution_x = 616  # 4x of 154px
scene.render.resolution_y = 616
scene.render.film_transparent = True
scene.render.filepath = '/tmp/titan_blender_base.png'

# Orthographic camera looking directly from front with slight 2.5D perspective tilt
cam_data = bpy.data.cameras.new('Camera')
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 2.05
cam = bpy.data.objects.new('Camera', cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam
cam.location = (0, -4, 0)
cam.rotation_euler = (math.radians(90), 0, 0)

# Create Outer Beveled Titanium Frame
bpy.ops.mesh.primitive_cube_add(size=1.92, location=(0, 0, 0))
outer = bpy.context.active_object
outer.scale = (1.0, 0.25, 1.0)
mod_bev = outer.modifiers.new('Bevel', 'BEVEL')
mod_bev.width = 0.14
mod_bev.segments = 6

mat_frame = bpy.data.materials.new('TitaniumFrame')
mat_frame.use_nodes = True
nodes = mat_frame.node_tree.nodes
bsdf_frame = nodes.get('Principled BSDF')
bsdf_frame.inputs['Base Color'].default_value = (0.75, 0.80, 0.85, 1.0)
bsdf_frame.inputs['Roughness'].default_value = 0.22
bsdf_frame.inputs['Metallic'].default_value = 0.95
outer.data.materials.append(mat_frame)

# Create Inner Obsidian Monolith Core
bpy.ops.mesh.primitive_cube_add(size=1.70, location=(0, -0.05, 0))
core = bpy.context.active_object
core.scale = (1.0, 0.25, 1.0)
mod_core_bev = core.modifiers.new('Bevel', 'BEVEL')
mod_core_bev.width = 0.04
mod_core_bev.segments = 4

mat_core = bpy.data.materials.new('ObsidianCore')
mat_core.use_nodes = True
bsdf_core = mat_core.node_tree.nodes.get('Principled BSDF')
bsdf_core.inputs['Base Color'].default_value = (0.012, 0.015, 0.022, 1.0)
bsdf_core.inputs['Roughness'].default_value = 0.05
bsdf_core.inputs['Metallic'].default_value = 0.4
core.data.materials.append(mat_core)

# Center seam vertical divider
bpy.ops.mesh.primitive_cube_add(size=0.03, location=(0, -0.18, 0))
seam = bpy.context.active_object
seam.scale = (1.0, 1.0, 50.0)
mat_seam = bpy.data.materials.new('Seam')
mat_seam.use_nodes = True
bsdf_seam = mat_seam.node_tree.nodes.get('Principled BSDF')
bsdf_seam.inputs['Base Color'].default_value = (0.005, 0.005, 0.008, 1.0)
bsdf_seam.inputs['Roughness'].default_value = 0.6
seam.data.materials.append(mat_seam)

# Studio Lights
# Key overhead left light
light_key = bpy.data.lights.new('Key', 'SUN')
light_key.energy = 4.5
l1 = bpy.data.objects.new('Key', light_key)
bpy.context.collection.objects.link(l1)
l1.rotation_euler = (math.radians(45), math.radians(-30), math.radians(20))

# Fill right rim light
light_fill = bpy.data.lights.new('FillRim', 'SUN')
light_fill.energy = 2.0
l2 = bpy.data.objects.new('FillRim', light_fill)
bpy.context.collection.objects.link(l2)
l2.rotation_euler = (math.radians(-30), math.radians(45), math.radians(-40))

# Bottom reflection bounce
light_bounce = bpy.data.lights.new('Bounce', 'POINT')
light_bounce.energy = 30.0
l3 = bpy.data.objects.new('Bounce', light_bounce)
l3.location = (0, -2, -1.5)
bpy.context.collection.objects.link(l3)

bpy.ops.render.render(write_still=True)
print("TITAN_RENDER_COMPLETE")
"""

with open('/tmp/render_titan.py', 'w') as f:
    f.write(blender_script)

print("Rendering Titan Monolith with Blender Cycles...")
p = subprocess.run(['/opt/homebrew/bin/blender', '-b', '-P', '/tmp/render_titan.py'], capture_output=True, text=True)
print(p.stdout[-150:])
