"""
Biometric City — Blender Scene
Run this in Blender's Scripting workspace (Scripting tab → Run Script).
Builds a photorealistic NYC city scene with:
  - PBR building materials (glass, brick, concrete, brownstone)
  - Procedural sky + HDRI-style world lighting
  - Animated ocean plane with Cycles-ready material
  - Emissive window glow (bloom-ready)
  - City uplighting with point lights
  - Volumetric atmosphere fog
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector

# ── Helpers ──────────────────────────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    # Clear orphan data
    for block in bpy.data.meshes:     bpy.data.meshes.remove(block)
    for block in bpy.data.materials:  bpy.data.materials.remove(block)
    for block in bpy.data.lights:     bpy.data.lights.remove(block)

def rng(seed, lo=0.0, hi=1.0):
    random.seed(seed)
    return lo + random.random() * (hi - lo)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

# ── Render Settings ───────────────────────────────────────────────────────────

def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False

    # Bloom via compositor
    scene.use_nodes = True
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = -0.3

    # Compositor: glare (bloom) node
    tree = scene.node_tree
    tree.nodes.clear()
    rn  = tree.nodes.new('CompositorNodeRLayers')
    rn.location = (0, 0)
    glare = tree.nodes.new('CompositorNodeGlare')
    glare.location = (300, 0)
    glare.glare_type = 'BLOOM'
    glare.threshold = 0.8
    glare.size = 8
    glare.mix = 0.5
    out = tree.nodes.new('CompositorNodeComposite')
    out.location = (600, 0)
    tree.links.new(rn.outputs['Image'],  glare.inputs['Image'])
    tree.links.new(glare.outputs['Image'], out.inputs['Image'])

# ── World / Sky ───────────────────────────────────────────────────────────────

def setup_world():
    world = bpy.data.worlds.new('CityWorld')
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    bg   = nt.nodes.new('ShaderNodeBackground')
    sky  = nt.nodes.new('ShaderNodeTexSky')
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(22)
    sky.sun_rotation   = math.radians(210)
    sky.air_density    = 1.0
    sky.dust_density   = 0.8
    sky.ozone_density  = 1.0
    out  = nt.nodes.new('ShaderNodeOutputWorld')

    bg.inputs['Strength'].default_value = 1.2
    nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

    # Atmosphere / fog volume
    vol_abs  = nt.nodes.new('ShaderNodeVolumeAbsorption')
    vol_scat = nt.nodes.new('ShaderNodeVolumeScatter')
    add_vol  = nt.nodes.new('ShaderNodeAddShader')
    vol_abs.inputs['Color'].default_value  = (0.04, 0.06, 0.10, 1.0)
    vol_abs.inputs['Density'].default_value = 0.0008
    vol_scat.inputs['Color'].default_value  = (0.55, 0.65, 0.80, 1.0)
    vol_scat.inputs['Density'].default_value = 0.0006
    nt.links.new(vol_abs.outputs['Volume'],  add_vol.inputs[0])
    nt.links.new(vol_scat.outputs['Volume'], add_vol.inputs[1])
    nt.links.new(add_vol.outputs['Shader'],  out.inputs['Volume'])

    sky.location   = (-400, 100)
    bg.location    = (-100, 100)
    vol_abs.location  = (-400, -100)
    vol_scat.location = (-400, -250)
    add_vol.location  = (-100, -175)
    out.location   = (200, 0)

# ── Materials ─────────────────────────────────────────────────────────────────

def make_glass_material(name, base_rgb, emissive_rgb=(1.0, 0.85, 0.45), emissive_strength=4.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value     = (*base_rgb, 1.0)
    bsdf.inputs['Metallic'].default_value       = 0.85
    bsdf.inputs['Roughness'].default_value      = 0.06
    bsdf.inputs['IOR'].default_value            = 1.52
    bsdf.inputs['Emission Color'].default_value = (*emissive_rgb, 1.0)
    bsdf.inputs['Emission Strength'].default_value = emissive_strength

    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def make_brick_material(name, base_rgb, emissive_strength=1.2):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    # Brick texture for surface detail
    coord  = nt.nodes.new('ShaderNodeTexCoord')
    mapping = nt.nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (8, 8, 8)
    brick  = nt.nodes.new('ShaderNodeTexBrick')
    brick.inputs['Color1'].default_value = (*base_rgb, 1.0)
    brick.inputs['Color2'].default_value = (
        base_rgb[0]*0.7, base_rgb[1]*0.7, base_rgb[2]*0.7, 1.0)
    brick.inputs['Mortar'].default_value = (0.12, 0.10, 0.09, 1.0)
    brick.inputs['Scale'].default_value  = 8.0
    brick.inputs['Mortar Size'].default_value = 0.04

    bump   = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.4

    bsdf   = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value        = 0.0
    bsdf.inputs['Roughness'].default_value       = 0.88
    bsdf.inputs['Emission Color'].default_value  = (1.0, 0.82, 0.42, 1.0)
    bsdf.inputs['Emission Strength'].default_value = emissive_strength

    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(coord.outputs['UV'],         mapping.inputs['Vector'])
    nt.links.new(mapping.outputs['Vector'],   brick.inputs['Vector'])
    nt.links.new(brick.outputs['Color'],      bsdf.inputs['Base Color'])
    nt.links.new(brick.outputs['Fac'],        bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'],      bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'],        out.inputs['Surface'])
    return mat

def make_concrete_material(name, base_rgb, emissive_strength=1.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    noise  = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value      = 25.0
    noise.inputs['Detail'].default_value     = 8.0
    noise.inputs['Roughness'].default_value  = 0.6
    noise.inputs['Distortion'].default_value = 0.2

    mix    = nt.nodes.new('ShaderNodeMixRGB')
    mix.inputs['Color1'].default_value = (*base_rgb, 1.0)
    mix.inputs['Color2'].default_value = (
        base_rgb[0]*0.82, base_rgb[1]*0.82, base_rgb[2]*0.82, 1.0)

    bsdf   = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value        = 0.02
    bsdf.inputs['Roughness'].default_value       = 0.75
    bsdf.inputs['Emission Color'].default_value  = (0.9, 0.78, 0.55, 1.0)
    bsdf.inputs['Emission Strength'].default_value = emissive_strength

    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(noise.outputs['Fac'],   mix.inputs['Fac'])
    nt.links.new(mix.outputs['Color'],   bsdf.inputs['Base Color'])
    nt.links.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def make_ground_material():
    mat = bpy.data.materials.new('WetAsphalt')
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value     = 80.0
    noise.inputs['Detail'].default_value    = 6.0
    noise.inputs['Roughness'].default_value = 0.55

    ramp  = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.03, 1.0)
    ramp.color_ramp.elements[1].color = (0.07, 0.07, 0.09, 1.0)

    bsdf  = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value   = 0.10
    bsdf.inputs['Roughness'].default_value  = 0.28   # wet = low roughness
    bsdf.inputs['Emission Color'].default_value = (0.08, 0.08, 0.14, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 0.5

    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(noise.outputs['Fac'],  ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    return mat

def make_ocean_material():
    mat = bpy.data.materials.new('Ocean')
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    wave   = nt.nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value      = 3.0
    wave.inputs['Distortion'].default_value = 6.0
    wave.inputs['Detail'].default_value     = 8.0
    wave.inputs['Detail Scale'].default_value = 3.0

    bump   = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.6
    bump.inputs['Distance'].default_value = 0.3

    bsdf   = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value     = (0.01, 0.04, 0.08, 1.0)
    bsdf.inputs['Metallic'].default_value       = 0.0
    bsdf.inputs['Roughness'].default_value      = 0.04
    bsdf.inputs['IOR'].default_value            = 1.333
    bsdf.inputs['Transmission Weight'].default_value = 0.95
    bsdf.inputs['Alpha'].default_value          = 0.92

    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(wave.outputs['Color'],   bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'],  bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    mat.blend_method = 'BLEND'
    return mat

# ── Building Generator ────────────────────────────────────────────────────────

GLASS_MATS = None
BRICK_MATS = None
CONC_MATS  = None

def init_materials():
    global GLASS_MATS, BRICK_MATS, CONC_MATS
    GLASS_MATS = [
        make_glass_material('GlassBlue',   hex_to_rgb('4a9ac8'), (0.50, 0.75, 1.00), 5.5),
        make_glass_material('GlassTeal',   hex_to_rgb('38a0b8'), (0.45, 0.80, 0.90), 5.0),
        make_glass_material('GlassDark',   hex_to_rgb('2a5070'), (0.55, 0.70, 1.00), 6.0),
    ]
    BRICK_MATS = [
        make_brick_material('BrickRed',    hex_to_rgb('c04828'), 1.5),
        make_brick_material('Brownstone',  hex_to_rgb('9a6840'), 1.2),
        make_brick_material('Warehouse',   hex_to_rgb('7a6858'), 1.0),
    ]
    CONC_MATS = [
        make_concrete_material('Limestone',  hex_to_rgb('e0cfa8'), 1.4),
        make_concrete_material('FinancialSt',hex_to_rgb('2a4a6a'), 4.0),
    ]

def add_building(x, z, w, d, h, mat, collection):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, z, h/2))
    obj = bpy.context.active_object
    obj.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    obj.name = f'Building_{x:.1f}_{z:.1f}'

    # Smooth shade
    bpy.ops.object.shade_smooth()
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = math.radians(60)

    # Cast and receive shadows
    obj.cycles.use_shadow_catcher = False
    obj.visible_shadow = True

    # Add to collection
    for c in obj.users_collection:
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def add_water_tower(parent_x, parent_z, roof_h, rng_seed):
    random.seed(rng_seed)
    ox = parent_x + random.uniform(-0.3, 0.3)
    oz = parent_z + random.uniform(-0.3, 0.3)

    mat = bpy.data.materials.new(f'WaterTower_{rng_seed}')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.22, 0.14, 0.08, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.9

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.22, depth=0.45,
        location=(ox, oz, roof_h + 0.45))
    tank = bpy.context.active_object
    tank.data.materials.append(mat)

    bpy.ops.mesh.primitive_cone_add(
        radius1=0.25, radius2=0, depth=0.22,
        location=(ox, oz, roof_h + 0.9))
    cap = bpy.context.active_object
    cap_mat = bpy.data.materials.new(f'Cap_{rng_seed}')
    cap_mat.use_nodes = True
    cap_bsdf = cap_mat.node_tree.nodes.get('Principled BSDF')
    if cap_bsdf:
        cap_bsdf.inputs['Base Color'].default_value = (0.06, 0.06, 0.06, 1.0)
    cap.data.materials.append(cap_mat)

# ── District Builder ──────────────────────────────────────────────────────────

DISTRICTS = [
    # key, cx, cz, sw, sd, count, h_lo, h_hi, w_lo, w_hi, mat_type, water_towers
    ('Financial',   -4, -52, 16, 16, 14, 12, 28, 1.4, 2.6, 'glass',  False),
    ('Tribeca',    -10, -37, 13, 13, 20,  3,  8, 0.9, 2.0, 'brick',  True),
    ('Midtown',      0,  12, 22, 22, 36,  8, 30, 1.2, 2.8, 'glass',  False),
    ('LowerEast',   14, -28, 14, 14, 26,  2,  5, 0.8, 1.6, 'brick',  True),
    ('Chelsea',    -15,   4, 12, 14, 20,  3,  9, 1.2, 2.5, 'conc',   True),
    ('UpperWest',  -16,  30, 14, 18, 24,  6, 14, 1.0, 2.2, 'conc',   True),
    ('Harlem',      -5,  46, 18, 18, 28,  2,  5, 0.9, 1.8, 'brick',  True),
    ('Brooklyn',    32, -50, 24, 22, 32,  2, 12, 0.9, 2.5, 'brick',  True),
    ('Williamsburg',38, -28, 14, 14, 22,  3, 16, 1.0, 2.5, 'conc',   True),
]

def build_city():
    init_materials()
    col = bpy.data.collections.new('NYC_City')
    bpy.context.scene.collection.children.link(col)

    for (name, cx, cz, sw, sd, count, h_lo, h_hi, w_lo, w_hi, mat_type, wt) in DISTRICTS:
        for i in range(count):
            seed = hash(name + str(i)) & 0xFFFFFF
            random.seed(seed)
            w  = random.uniform(w_lo, w_hi)
            d  = random.uniform(w_lo, w_hi)
            h  = random.uniform(h_lo, h_hi)
            px = cx + random.uniform(-sw/2, sw/2)
            pz = cz + random.uniform(-sd/2, sd/2)

            if mat_type == 'glass':
                mat = random.choice(GLASS_MATS)
            elif mat_type == 'brick':
                mat = random.choice(BRICK_MATS)
            else:
                mat = random.choice(CONC_MATS)

            add_building(px, pz, w, d, h, mat, col)

            if wt and h > 4 and random.random() > 0.55:
                add_water_tower(px, pz, h, seed)

# ── Ground Plane ──────────────────────────────────────────────────────────────

def add_ground():
    bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = 'GroundPlane'
    ground.data.materials.append(make_ground_material())

def add_ocean():
    bpy.ops.mesh.primitive_plane_add(size=700, location=(0, 0, -0.8))
    ocean_obj = bpy.context.active_object
    ocean_obj.name = 'Ocean'

    # Add ocean modifier for waves
    mod = ocean_obj.modifiers.new('Ocean', 'OCEAN')
    mod.resolution = 8
    mod.wave_scale = 1.2
    mod.wave_scale_min = 0.2
    mod.wind_velocity = 5.0
    mod.choppiness = 0.8
    mod.use_foam = True

    ocean_obj.data.materials.append(make_ocean_material())

# ── Lighting ──────────────────────────────────────────────────────────────────

def add_lighting():
    # Sun
    bpy.ops.object.light_add(type='SUN', location=(60, 80, 100))
    sun = bpy.context.active_object
    sun.name = 'CitySun'
    sun.data.energy = 4.5
    sun.data.color  = (1.0, 0.97, 0.88)
    sun.data.angle  = math.radians(0.8)
    sun.rotation_euler = (math.radians(45), 0, math.radians(30))

    # City glow uplights (warm orange from streets)
    glow_positions = [
        (0,   0,   2.0, (1.0, 0.47, 0.13), 800),
        (20,  20,  2.0, (1.0, 0.60, 0.20), 400),
        (-20,-20,  2.0, (1.0, 0.55, 0.15), 350),
        (15, -30,  2.0, (1.0, 0.52, 0.18), 300),
        (-15, 25,  2.0, (1.0, 0.50, 0.12), 280),
    ]
    for i, (x, y, z, color, energy) in enumerate(glow_positions):
        bpy.ops.object.light_add(type='POINT', location=(x, y, z))
        light = bpy.context.active_object
        light.name = f'CityGlow_{i}'
        light.data.energy = energy
        light.data.color  = color
        light.data.shadow_soft_size = 8.0
        light.data.use_shadow = True

    # Cool fill from sky side (blue ambient sky bounce)
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 120))
    sky_fill = bpy.context.active_object
    sky_fill.name = 'SkyFill'
    sky_fill.data.energy = 200
    sky_fill.data.color  = (0.55, 0.70, 1.0)
    sky_fill.data.size   = 200

# ── Camera ────────────────────────────────────────────────────────────────────

def setup_camera():
    bpy.ops.object.camera_add(location=(45, -90, 65))
    cam = bpy.context.active_object
    cam.name = 'CityCamera'
    cam.rotation_euler = (math.radians(52), 0, math.radians(28))
    cam.data.lens = 35
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 95
    cam.data.dof.aperture_fstop = 4.0
    bpy.context.scene.camera = cam

# ── Run Everything ────────────────────────────────────────────────────────────

print("Clearing scene...")
clear_scene()

print("Setting up render...")
setup_render()

print("Setting up world / sky...")
setup_world()

print("Building city...")
build_city()

print("Adding ground + ocean...")
add_ground()
add_ocean()

print("Adding lighting...")
add_lighting()

print("Setting up camera...")
setup_camera()

print("\n✅ Biometric City scene built!")
print("   • Press F12 to render")
print("   • Use Viewport Shading = Rendered (Z → Rendered) to preview")
print("   • Scene uses Cycles with 128 samples + denoising")
