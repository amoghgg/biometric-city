"""
NYC Landmarks for Biometric City
Builds: Statue of Liberty, Brooklyn Bridge, NYC Harbor + Skyline
Run in Blender Scripting workspace or via MCP socket
"""
import bpy, math, random
from mathutils import Vector

# ─── Helpers ─────────────────────────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for d in [bpy.data.meshes, bpy.data.materials, bpy.data.lights,
              bpy.data.curves, bpy.data.cameras]:
        for b in list(d): d.remove(b)

def mk_mat(name, color, rough=0.8, metal=0.0, emit=None, emit_str=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value      = (*color, 1.0)
        b.inputs['Roughness'].default_value       = rough
        b.inputs['Metallic'].default_value        = metal
        if emit and emit_str > 0:
            b.inputs['Emission Color'].default_value  = (*emit, 1.0)
            b.inputs['Emission Strength'].default_value = emit_str
    return m

def lnk(col, obj):
    for c in obj.users_collection: c.objects.unlink(obj)
    col.objects.link(obj)
    return obj

def bx(col, name, loc, sc, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name
    o.scale = sc; o.rotation_euler = rot
    bpy.ops.object.transform_apply(scale=True, rotation=any(r!=0 for r in rot))
    o.data.materials.append(mat); return lnk(col, o)

def cy(col, name, loc, r, h, mat, rot=(0,0,0), seg=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=seg, location=loc)
    o = bpy.context.active_object; o.name = name
    if any(r_!=0 for r_ in rot):
        o.rotation_euler = rot
        bpy.ops.object.transform_apply(rotation=True)
    o.data.materials.append(mat); return lnk(col, o)

def cn(col, name, loc, r1, r2, h, mat, rot=(0,0,0), seg=12):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=h, vertices=seg, location=loc)
    o = bpy.context.active_object; o.name = name
    if any(r_!=0 for r_ in rot):
        o.rotation_euler = rot
        bpy.ops.object.transform_apply(rotation=True)
    o.data.materials.append(mat); return lnk(col, o)

def sp(col, name, loc, r, mat, seg=12):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=8)
    o = bpy.context.active_object; o.name = name
    o.data.materials.append(mat); return lnk(col, o)

def tr(col, name, loc, major_r, minor_r, mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_r, minor_radius=minor_r,
                                      major_segments=24, minor_segments=8, location=loc)
    o = bpy.context.active_object; o.name = name
    o.data.materials.append(mat); return lnk(col, o)

# ─── Statue of Liberty (at origin offset) ────────────────────────────────────

def build_sol(ox=0, oy=0):
    col = bpy.data.collections.new('StatueOfLiberty')
    bpy.context.scene.collection.children.link(col)

    MV  = mk_mat('SOL_Verdigris', (0.18, 0.47, 0.38), rough=0.62, metal=0.25)
    MG  = mk_mat('SOL_Granite',   (0.50, 0.47, 0.43), rough=0.88)
    MT  = mk_mat('SOL_Torch',     (1.0, 0.88, 0.22), rough=0.15, metal=0.9,
                  emit=(1.0, 0.72, 0.1), emit_str=10.0)
    MGL = mk_mat('SOL_Gold',      (0.85, 0.70, 0.18), rough=0.12, metal=0.95)
    MI  = mk_mat('SOL_Island',    (0.12, 0.34, 0.10), rough=0.95)
    MW  = mk_mat('SOL_CrownWin',  (0.65, 0.88, 1.0),  rough=0.05,
                  emit=(0.6, 0.9, 1.0), emit_str=2.5)
    MFG = mk_mat('SOL_FlameGlow', (1.0, 0.65, 0.05), rough=0.3,
                  emit=(1.0, 0.6, 0.05), emit_str=15.0)
    MINK= mk_mat('SOL_Ink',       (0.08, 0.06, 0.05), rough=0.95)

    # Liberty Island terrain
    bpy.ops.mesh.primitive_cylinder_add(radius=10, depth=1.0, vertices=10, location=(ox, oy, 0.5))
    isle = bpy.context.active_object; isle.name = 'SOL_Island'; isle.data.materials.append(MI); lnk(col, isle)

    # Dock/pier jutting south
    bx(col, 'SOL_Dock', (ox, oy-11, 0.3), (3.0, 4.0, 0.3), MG)
    bx(col, 'SOL_DockRamp', (ox, oy-7, 0.25), (2.0, 3.0, 0.25), MG)

    # Seawall (low retaining wall around island)
    for i in range(10):
        angle = i / 10 * math.pi * 2
        wx = ox + math.cos(angle) * 9.5; wy = oy + math.sin(angle) * 9.5
        bx(col, f'SOL_Wall_{i}', (wx, wy, 0.6), (0.4, 1.8, 0.8), MG)

    # Star-shaped fort base (octagonal)
    bpy.ops.mesh.primitive_cylinder_add(radius=7, depth=4.5, vertices=8, location=(ox, oy, 3.0))
    fort = bpy.context.active_object; fort.name = 'SOL_Fort'; fort.data.materials.append(MG); lnk(col, fort)
    fort.rotation_euler.z = math.radians(22.5)
    bpy.ops.object.transform_apply(rotation=True)

    # Fort crenellation teeth on top
    for i in range(16):
        angle = i / 16 * math.pi * 2
        cx_ = ox + math.cos(angle) * 6.5; cy_ = oy + math.sin(angle) * 6.5
        if i % 2 == 0:
            bx(col, f'SOL_Cren_{i}', (cx_, cy_, 5.5), (0.6, 0.6, 0.6), MG)

    # Pedestal — 3 stepped tiers (granite)
    bx(col, 'SOL_Ped0',   (ox, oy, 5.8),  (9.5, 9.5, 0.8), MG)   # wide skirting
    bx(col, 'SOL_Ped1',   (ox, oy, 7.0),  (7.8, 7.8, 1.6), MG)
    bx(col, 'SOL_Ped2',   (ox, oy, 9.1),  (6.0, 6.0, 2.2), MG)
    bx(col, 'SOL_Ped3',   (ox, oy, 11.0), (4.5, 4.5, 0.8), MG)   # top ledge

    # Balcony cornice
    bx(col, 'SOL_Balcony', (ox, oy, 11.6), (5.5, 5.5, 0.25), MG)
    # Balcony railing posts
    for i in range(12):
        angle = i / 12 * math.pi * 2
        rx = ox + math.cos(angle) * 2.6; ry = oy + math.sin(angle) * 2.6
        cy(col, f'SOL_Post_{i}', (rx, ry, 12.0), 0.055, 0.6, MG, seg=6)
    tr(col, 'SOL_BalconyRail', (ox, oy, 12.25), 2.6, 0.05, MG)

    # Horizontal string courses on pedestal
    for z_ in [6.6, 8.2, 10.1]:
        bx(col, f'SOL_Course_{z_}', (ox, oy, z_), (8.0-z_*0.3, 8.0-z_*0.3, 0.15), MG)

    # ── Statue body ────────────────────────────────────────────────────────────
    z0 = 12.0  # statue base Z

    # Robe hem — wide flare
    cn(col, 'SOL_Hem',    (ox, oy, z0+1.0), 2.8, 2.0, 2.0, MV, seg=18)
    # Lower skirt
    cy(col, 'SOL_Skirt',  (ox, oy, z0+3.5), 1.9, 5.0, MV, seg=16)
    # Waist cinch
    cy(col, 'SOL_Waist',  (ox, oy, z0+6.2), 1.55, 1.0, MV, seg=14)
    # Torso widening to chest
    cn(col, 'SOL_Torso',  (ox, oy, z0+7.8), 1.45, 1.55, 3.0, MV, seg=14)
    # Chest
    cy(col, 'SOL_Chest',  (ox, oy, z0+9.8), 1.55, 2.5, MV, seg=14)

    # Drapery folds on front (thin flat fins)
    for i in range(5):
        fz = z0 + 2.0 + i * 1.0
        bx(col, f'SOL_DrapeFold_{i}',
           (ox + 0.5*(i%3-1)*0.4, oy + 1.85, fz),
           (0.18, 0.06, 0.55 - i*0.04), MV,
           rot=(0, 0, math.radians(5*(i-2))))

    # Neck
    cy(col, 'SOL_Neck',   (ox, oy, z0+11.5), 0.52, 1.0, MV, seg=10)
    # Head — slightly elongated sphere
    sp(col, 'SOL_Head',   (ox, oy, z0+12.7), 0.92, MV, seg=16)
    # Brow ridge, cheekbones (subtle boxes)
    bx(col, 'SOL_Brow',  (ox, oy+0.85, z0+13.1), (1.1, 0.12, 0.12), MV)
    bx(col, 'SOL_NoseBridge', (ox, oy+0.9, z0+12.75), (0.2, 0.1, 0.3), MV)
    # Nose
    cn(col, 'SOL_Nose',  (ox, oy+0.98, z0+12.65), 0.1, 0.03, 0.3, MV, seg=6)
    # Chin
    sp(col, 'SOL_Chin',  (ox, oy+0.6, z0+12.25), 0.22, MV, seg=6)
    # Hair/waves at sides
    for s, side in [(-1, 'L'), (1, 'R')]:
        cy(col, f'SOL_Hair_{side}', (ox + s*0.82, oy-0.1, z0+12.4), 0.18, 0.9, MV, seg=8)
        cy(col, f'SOL_HairB_{side}',(ox + s*0.6, oy-0.4, z0+12.1), 0.14, 0.6, MV, seg=8)

    # Crown ring
    tr(col, 'SOL_CrownRing', (ox, oy, z0+13.55), 0.78, 0.14, MV)
    # Crown band
    cy(col, 'SOL_CrownBand', (ox, oy, z0+13.55), 0.78, 0.22, MV, seg=24)

    # 7 Crown spikes
    for i in range(7):
        angle = i / 7 * math.pi * 2
        sx = ox + math.cos(angle) * 0.78
        sy = oy + math.sin(angle) * 0.78
        lean_x = math.radians(22) * math.cos(angle)
        lean_y = math.radians(22) * math.sin(angle)
        cn(col, f'SOL_Spike_{i}', (sx, sy, z0+14.05),
           0.12, 0.01, 1.4, MV, rot=(lean_x, lean_y, 0), seg=7)

    # Crown windows between spikes
    for i in range(7):
        angle = i / 7 * math.pi * 2 + math.pi / 14
        wx = ox + math.cos(angle) * 0.74
        wy = oy + math.sin(angle) * 0.74
        bx(col, f'SOL_CWin_{i}', (wx, wy, z0+13.55), (0.13, 0.07, 0.3), MW)

    # ── Right arm (torch arm, raised up-right) ──────────────────────────────
    # Upper arm angles up and to right
    cy(col, 'SOL_RArm1', (ox+1.2, oy, z0+10.5), 0.34, 3.2, MV,
       rot=(0, math.radians(-55), 0), seg=10)
    # Elbow sphere
    sp(col, 'SOL_RElbow', (ox+2.2, oy, z0+11.8), 0.32, MV, seg=8)
    # Forearm — nearly vertical
    cy(col, 'SOL_RArm2', (ox+2.45, oy, z0+13.5), 0.28, 3.2, MV,
       rot=(math.radians(6), math.radians(-8), 0), seg=10)
    # Drapery sleeve folds
    for i in range(4):
        zf = z0 + 10.0 + i * 0.7
        cn(col, f'SOL_SlvFold_{i}',
           (ox + 0.5 + i*0.3, oy, zf), 0.18-i*0.02, 0.12, 0.4, MV, seg=8)
    # Wrist
    cy(col, 'SOL_RWrist', (ox+2.75, oy, z0+15.3), 0.22, 0.5, MV, seg=8)
    # Fist
    sp(col, 'SOL_RFist',  (ox+2.9, oy, z0+15.9), 0.3, MV, seg=8)

    # Torch
    cy(col, 'SOL_TorchHandle', (ox+2.9, oy, z0+17.0), 0.13, 2.0, MGL, seg=8)
    # Flame bowl
    cn(col, 'SOL_TorchBowl',   (ox+2.9, oy, z0+18.2), 0.38, 0.15, 0.7, MGL, seg=14)
    # Flame shaft taper
    cn(col, 'SOL_Flame',       (ox+2.9, oy, z0+18.9), 0.28, 0.02, 1.0, MT, seg=10)
    # Inner glow
    sp(col, 'SOL_FlameCore',   (ox+2.9, oy, z0+18.6), 0.22, MFG, seg=8)
    # Outer glow halo (larger transparent sphere)
    sp(col, 'SOL_FlameHalo',   (ox+2.9, oy, z0+18.7), 0.38,
       mk_mat('SOL_FlameHalo', (1.0, 0.8, 0.2), rough=0.5,
              emit=(1.0, 0.65, 0.1), emit_str=6.0), seg=8)

    # ── Left arm (tablet arm, lowered and forward) ───────────────────────────
    cy(col, 'SOL_LArm1', (ox-1.25, oy+0.3, z0+10.0), 0.30, 2.8, MV,
       rot=(math.radians(30), math.radians(18), 0), seg=10)
    sp(col, 'SOL_LElbow', (ox-1.9, oy+0.8, z0+11.4), 0.28, MV, seg=8)
    cy(col, 'SOL_LArm2', (ox-2.2, oy+1.0, z0+12.5), 0.25, 2.2, MV,
       rot=(math.radians(12), math.radians(8), 0), seg=10)
    # Tablet
    bx(col, 'SOL_Tablet', (ox-2.9, oy+1.4, z0+11.5), (0.95, 0.16, 1.35), MG,
       rot=(0.2, 0.0, -0.38))
    # Tablet inscription lines (JULY IV MDCCLXXVI)
    for ti in range(4):
        bx(col, f'SOL_Text_{ti}',
           (ox-2.95, oy+1.56, z0+11.2 + ti*0.28),
           (0.7, 0.02, 0.045), MINK)
    # Roman numeral divider
    bx(col, 'SOL_TextDiv', (ox-2.95, oy+1.56, z0+11.05), (0.5, 0.02, 0.08), MINK)

    # ── Ankle chains / broken shackles ──────────────────────────────────────
    chain_z = z0 + 0.6
    for i in range(3):
        angle = i * math.pi * 2 / 3
        cx_ = ox + math.cos(angle) * 1.2; cy_ = oy + math.sin(angle) * 1.2
        tr(col, f'SOL_ChainLink_{i}', (cx_, cy_, chain_z), 0.2, 0.06,
           mk_mat('SOL_Chain', (0.25, 0.22, 0.20), rough=0.75, metal=0.5))

    print(f"  ✓ Statue of Liberty at ({ox:.0f}, {oy:.0f}), height ~{z0+19.9:.1f} units")

# ─── Brooklyn Bridge ─────────────────────────────────────────────────────────

def build_brooklyn_bridge(bx_=10, by=0):
    col = bpy.data.collections.new('BrooklynBridge')
    bpy.context.scene.collection.children.link(col)

    MS  = mk_mat('BB_Stone',      (0.70, 0.65, 0.56), rough=0.88)
    MST = mk_mat('BB_Steel',      (0.30, 0.32, 0.35), rough=0.45, metal=0.7)
    MR  = mk_mat('BB_Road',       (0.14, 0.13, 0.12), rough=0.92)
    MRC = mk_mat('BB_RoadCrack',  (0.10, 0.09, 0.08), rough=0.95)
    MR2 = mk_mat('BB_Railing',    (0.40, 0.42, 0.45), rough=0.55, metal=0.6)
    MCA = mk_mat('BB_Cable',      (0.28, 0.30, 0.32), rough=0.60, metal=0.8)
    MAN = mk_mat('BB_Anchor',     (0.55, 0.50, 0.44), rough=0.86)

    # Bridge axis: runs along local Y from y=-36 (Manhattan) to y=+36 (Brooklyn)
    # Tower positions at y=-18 and y=+18
    # Deck at Z=7, tower tops at Z=15

    DECK_Z   = 7.0
    TOWER_Y  = [-18, 18]
    TOWER_H  = 15.5
    SPAN_LEN = 36.0  # half span

    # ── Towers ────────────────────────────────────────────────────────────────
    for ti, ty in enumerate(TOWER_Y):
        prefix = f'BB_T{ti}'

        # Two main pylon shafts
        for sx, side in [(-2.0, 'L'), (2.0, 'R')]:
            # Main shaft (tapers slightly)
            bx(col, f'{prefix}_{side}_Shaft',
               (bx_+sx, by+ty, TOWER_H/2), (1.35, 1.5, TOWER_H), MS)
            # Pointed top cap (Gothic)
            cn(col, f'{prefix}_{side}_Cap',
               (bx_+sx, by+ty, TOWER_H+1.2), 1.3, 0.08, 2.4, MS, seg=4)
            # Finial ball
            sp(col, f'{prefix}_{side}_Finial',
               (bx_+sx, by+ty, TOWER_H+2.6), 0.25, MS, seg=8)

        # Cross arch between pylons — pointed Gothic arch
        # Arch springer (lower horizontal)
        bx(col, f'{prefix}_Springer', (bx_, by+ty, 5.0), (5.2, 1.5, 0.5), MS)
        # Arch haunches — gradually narrowing toward keystone
        for az, asc in [(6.0, 4.5), (7.5, 3.8), (9.0, 2.8), (10.5, 1.8), (11.8, 0.9)]:
            bx(col, f'{prefix}_ArchVoid_{az}',
               (bx_, by+ty, az), (asc, 1.52, 0.55), MS)
        # Keystone
        bx(col, f'{prefix}_Keystone', (bx_, by+ty, 12.8), (0.5, 1.55, 0.6), MS)

        # Upper arch (smaller, near top)
        bx(col, f'{prefix}_ArchHi', (bx_, by+ty, 12.5), (4.6, 1.5, 0.4), MS)
        for az2, asc2 in [(13.0, 3.5), (13.8, 2.2), (14.4, 0.8)]:
            bx(col, f'{prefix}_ArchHi_{az2}',
               (bx_, by+ty, az2), (asc2, 1.52, 0.38), MS)

        # Horizontal bands / string courses
        for bz in [3.0, 6.5, 11.0, 14.0]:
            bx(col, f'{prefix}_Band_{bz}',
               (bx_, by+ty, bz), (5.0, 1.6, 0.22), MS)

        # Cable saddle plates on top
        for sx in [-2.0, 2.0]:
            bx(col, f'{prefix}_Saddle_{sx}',
               (bx_+sx, by+ty, TOWER_H+0.15), (1.6, 1.2, 0.4), MST)

    # ── Anchorage blocks ─────────────────────────────────────────────────────
    for ay, name in [(-38, 'Manhattan'), (38, 'Brooklyn')]:
        bx(col, f'BB_Anc_{name}', (bx_, by+ay, 2.5), (8.0, 5.5, 5.0), MAN)
        # Anchor eyes
        for sx in [-2.0, 2.0]:
            cy(col, f'BB_AncEye_{name}_{sx}', (bx_+sx, by+ay, 4.5), 0.45, 1.5, MST,
               rot=(math.radians(90), 0, 0), seg=10)

    # ── Main deck structure ───────────────────────────────────────────────────
    # Approach ramps (sloped)
    bx(col, 'BB_Ramp_Man', (bx_, by-29, 4.0), (5.5, 8.0, 0.5), MR,
       rot=(math.radians(9), 0, 0))
    bx(col, 'BB_Ramp_Bkn', (bx_, by+29, 4.0), (5.5, 8.0, 0.5), MR,
       rot=(math.radians(-9), 0, 0))
    # Main span
    bx(col, 'BB_Deck',     (bx_, by, DECK_Z), (5.5, SPAN_LEN*2, 0.45), MR)
    # Center line / divider
    bx(col, 'BB_Center',   (bx_, by, DECK_Z+0.24), (0.15, SPAN_LEN*2, 0.08), MRC)
    # Sidewalks
    for sx in [-2.2, 2.2]:
        bx(col, f'BB_Sidewalk_{sx}', (bx_+sx, by, DECK_Z+0.28), (1.0, SPAN_LEN*2, 0.12), MRC)

    # Deck railing
    for sx in [-3.0, 3.0]:
        for seg_y in range(-35, 36, 3):
            cy(col, f'BB_Rail_{sx}_{seg_y}',
               (bx_+sx, by+seg_y, DECK_Z+0.9), 0.06, 1.2, MR2, seg=6)
        bx(col, f'BB_RailTop_{sx}', (bx_+sx, by, DECK_Z+1.5), (0.1, SPAN_LEN*2, 0.1), MR2)

    # Floor deck truss (cross-beams visible below deck)
    for y_truss in range(-35, 36, 4):
        bx(col, f'BB_Truss_{y_truss}', (bx_, by+y_truss, DECK_Z-0.4),
           (6.5, 0.25, 0.4), MST)

    # ── Main suspension cables (parabolic catenary) ───────────────────────────
    # Build using many small cylinder segments following a parabola
    for cxo in [-2.0, 2.0]:
        # y from -38 to +38 anchors, dip at y=0
        # Cable height: h(y) = DECK_Z + (y/18)^2 * (TOWER_H - DECK_Z) but pass thru tower tops
        # h(±18) = TOWER_H = 15.5, h(0) = DECK_Z + sag = ~5.5
        SAG_Z   = 5.5
        STEPS   = 40
        pts = []
        for si in range(STEPS + 1):
            y_c = -38 + si * 76 / STEPS
            # Parabola: 0 at y=0 (sag), TOWER_H at y=±18, back down to anchor at ±38
            if abs(y_c) <= 18:
                t = y_c / 18
                z_c = SAG_Z + (TOWER_H - SAG_Z) * t * t
            else:
                t = (abs(y_c) - 18) / 20
                z_c = TOWER_H - (TOWER_H - 3.5) * t
            pts.append(Vector((bx_+cxo, by+y_c, z_c)))

        for si in range(len(pts)-1):
            p1, p2 = pts[si], pts[si+1]
            mid = (p1 + p2) / 2
            seg_vec = p2 - p1
            length = seg_vec.length
            # Create cylinder
            bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=length,
                                                 vertices=6, location=mid)
            cable_seg = bpy.context.active_object
            cable_seg.name = f'BB_MainCable_{cxo}_{si}'
            # Orient along segment
            rot_q = seg_vec.normalized().to_track_quat('Z', 'Y')
            cable_seg.rotation_euler = rot_q.to_euler()
            bpy.ops.object.transform_apply(rotation=True)
            cable_seg.data.materials.append(MCA)
            lnk(col, cable_seg)

    # ── Hanger cables (vertical from main cable to deck) ─────────────────────
    SAG_Z = 5.5
    for y_h in range(-17, 18, 2):
        for cxo in [-2.0, 2.0]:
            # Main cable height at this y
            if abs(y_h) <= 18:
                t = y_h / 18
                z_cable = SAG_Z + (TOWER_H - SAG_Z) * t * t
            else:
                z_cable = DECK_Z + 0.5
            z_deck = DECK_Z + 0.2
            if z_cable > z_deck + 0.3:
                h_hanger = z_cable - z_deck
                cy(col, f'BB_Hanger_{cxo}_{y_h}',
                   (bx_+cxo, by+y_h, (z_cable+z_deck)/2),
                   0.028, h_hanger, MCA, seg=4)

    # ── Diagonal stays from towers ────────────────────────────────────────────
    for ti, ty in enumerate(TOWER_Y):
        for di in range(1, 9):
            y_dir = -1 if ti == 0 else 1
            y_stay = ty + di * y_dir * 1.8
            if abs(y_stay) > SPAN_LEN + 2:
                break
            z_top  = TOWER_H - 0.5
            z_bot  = DECK_Z + 0.3
            for cxo in [-2.0, 2.0]:
                p1 = Vector((bx_+cxo, by+ty, z_top))
                p2 = Vector((bx_+cxo, by+y_stay, z_bot))
                mid = (p1 + p2) / 2
                seg_vec = p2 - p1
                length = seg_vec.length
                bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=length,
                                                     vertices=5, location=mid)
                stay = bpy.context.active_object
                stay.name = f'BB_Stay_{ti}_{di}_{cxo}'
                rot_q = seg_vec.normalized().to_track_quat('Z', 'Y')
                stay.rotation_euler = rot_q.to_euler()
                bpy.ops.object.transform_apply(rotation=True)
                stay.data.materials.append(MCA)
                lnk(col, stay)

    print("  ✓ Brooklyn Bridge built")

# ─── NYC Harbor Water ─────────────────────────────────────────────────────────

def build_harbor():
    bpy.ops.mesh.primitive_plane_add(size=500, location=(0, 0, -0.6))
    water = bpy.context.active_object; water.name = 'NYCHarbor'

    # Subdivide for gentle wave sim
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.subdivide(number_cuts=30)
    bpy.ops.object.editmode_toggle()

    mod = water.modifiers.new('HarborWave', 'WAVE')
    mod.height = 0.4; mod.width = 4.0; mod.speed = 0.4; mod.start_position_object = None

    MWater = mk_mat('Harbor', (0.01, 0.04, 0.10), rough=0.04, metal=0.0,
                    emit=(0.02, 0.06, 0.12), emit_str=0.5)
    water.data.materials.append(MWater)
    print("  ✓ Harbor water built")

# ─── Liberty Island seabed + shoreline rocks ──────────────────────────────────

def build_shoreline():
    col = bpy.data.collections.new('Shoreline')
    bpy.context.scene.collection.children.link(col)
    MRock = mk_mat('Rock', (0.22, 0.21, 0.19), rough=0.92)
    MGravel = mk_mat('Gravel', (0.30, 0.28, 0.25), rough=0.97)
    random.seed(77)
    for i in range(40):
        angle = i / 40 * math.pi * 2
        r_r = 8.5 + random.uniform(-1.5, 1.5)
        rx = math.cos(angle) * r_r; ry = math.sin(angle) * r_r
        rs = random.uniform(0.3, 0.9)
        sp(col, f'Rock_{i}', (rx, ry, -0.2), rs, MRock, seg=6)
    # Concrete dock structure
    bx(col, 'Dock_Slab', (0, -12, -0.3), (3.5, 5.0, 0.35), mk_mat('Dock', (0.40, 0.38, 0.35), rough=0.88))
    for i in range(4):
        cy(col, f'Dock_Pylon_{i}', (-1.2+i*0.8, -13.5, -1.2), 0.18, 2.0,
           mk_mat('DockPylon', (0.35, 0.33, 0.30), rough=0.9), seg=6)

# ─── NYC Background Skyline ───────────────────────────────────────────────────

def build_skyline():
    col = bpy.data.collections.new('NYCSkyline')
    bpy.context.scene.collection.children.link(col)

    GL = mk_mat('Sky_Glass',  (0.22, 0.38, 0.58), rough=0.08, metal=0.75,
                emit=(0.5, 0.75, 1.0), emit_str=2.0)
    BR = mk_mat('Sky_Brick',  (0.55, 0.40, 0.32), rough=0.87,
                emit=(1.0, 0.85, 0.50), emit_str=1.2)
    LM = mk_mat('Sky_Lime',   (0.72, 0.68, 0.58), rough=0.84,
                emit=(1.0, 0.90, 0.60), emit_str=1.5)
    DG = mk_mat('Sky_DkGlass',(0.12, 0.18, 0.30), rough=0.05, metal=0.85,
                emit=(0.4, 0.7, 1.0), emit_str=3.0)
    mats = [GL, BR, LM, DG]

    random.seed(99)
    # Manhattan skyline cluster (behind bridge, to the south)
    for i in range(80):
        x = random.uniform(-55, 55)
        y = random.uniform(-100, -60)
        w = random.uniform(1.2, 5.5)
        d = random.uniform(1.2, 5.5)
        h = random.uniform(4, 42)
        m = random.choice(mats)
        bpy.ops.mesh.primitive_cube_add(location=(x, y, h/2))
        o = bpy.context.active_object; o.scale = (w, d, h)
        bpy.ops.object.transform_apply(scale=True)
        o.data.materials.append(m); lnk(col, o)

        # Setback top
        if h > 20 and random.random() > 0.4:
            tw = w * 0.6; td = d * 0.6; th = random.uniform(4, 12)
            bpy.ops.mesh.primitive_cube_add(location=(x, y, h + th/2))
            ot = bpy.context.active_object; ot.scale = (tw, td, th)
            bpy.ops.object.transform_apply(scale=True)
            ot.data.materials.append(m); lnk(col, ot)

        # Water towers on some
        if random.random() > 0.65 and h > 8:
            wtx = x + random.uniform(-w*0.3, w*0.3)
            wty = y + random.uniform(-d*0.3, d*0.3)
            cy(col, f'Sky_WT_{i}', (wtx, wty, h+0.4), 0.24, 0.5, BR, seg=10)
            cn(col, f'Sky_WTCap_{i}', (wtx, wty, h+0.75), 0.28, 0.01, 0.3,
               mk_mat(f'WTCap_{i}', (0.06, 0.06, 0.06), rough=0.9), seg=10)

    # Brooklyn side (far side of bridge)
    for i in range(35):
        x = random.uniform(-40, 40)
        y = random.uniform(55, 90)
        w = random.uniform(1.0, 3.5)
        d = random.uniform(1.0, 3.5)
        h = random.uniform(2, 14)
        bpy.ops.mesh.primitive_cube_add(location=(x, y, h/2))
        o = bpy.context.active_object; o.scale = (w, d, h)
        bpy.ops.object.transform_apply(scale=True)
        o.data.materials.append(random.choice(mats)); lnk(col, o)

    print("  ✓ NYC skyline built")

# ─── Street-level details ─────────────────────────────────────────────────────

def build_street_details():
    col = bpy.data.collections.new('StreetDetails')
    bpy.context.scene.collection.children.link(col)
    MRd = mk_mat('Street', (0.10, 0.10, 0.11), rough=0.85)
    MSW = mk_mat('Sidewalk',(0.38, 0.36, 0.34), rough=0.90)
    MCb = mk_mat('Curb',    (0.30, 0.29, 0.27), rough=0.88)
    MYL = mk_mat('YellowLine',(0.9, 0.85, 0.1), rough=0.85,
                 emit=(0.9, 0.85, 0.1), emit_str=0.4)

    # Main avenue
    bx(col, 'Avenue_Main', (0, -65, -0.05), (8.0, 60.0, 0.15), MRd)
    bx(col, 'Sidewalk_E',  (5.5, -65, -0.05), (3.5, 60.0, 0.1), MSW)
    bx(col, 'Sidewalk_W',  (-5.5,-65, -0.05), (3.5, 60.0, 0.1), MSW)
    # Yellow center line dashes
    for di in range(20):
        bx(col, f'YLine_{di}', (0, -95 + di*3.0, 0.01), (0.15, 1.5, 0.04), MYL)

    # Street lamps along avenue
    MLP = mk_mat('LampPole', (0.20, 0.20, 0.22), rough=0.7, metal=0.5)
    MLG = mk_mat('LampGlow', (1.0, 0.95, 0.7), rough=0.2,
                 emit=(1.0, 0.95, 0.7), emit_str=8.0)
    for li in range(10):
        lx = 6.5 if li % 2 == 0 else -6.5
        ly = -95 + li * 6.0
        cy(col, f'Lamp_Pole_{li}', (lx, ly, 2.2), 0.08, 4.5, MLP, seg=6)
        sp(col, f'Lamp_Globe_{li}', (lx, ly, 4.7), 0.22, MLG, seg=6)
        # Arm
        bx(col, f'Lamp_Arm_{li}', (lx - 0.2*(1 if lx>0 else -1), ly, 4.3),
           (0.6, 0.06, 0.06), MLP)

    # Fire hydrants
    MHyd = mk_mat('Hydrant', (0.85, 0.12, 0.08), rough=0.75)
    for hi in range(6):
        hx = 4.8 if hi%2==0 else -4.8
        hy = -95 + hi * 10
        cy(col, f'Hydrant_Body_{hi}', (hx, hy, 0.25), 0.13, 0.4, MHyd, seg=8)
        cy(col, f'Hydrant_Top_{hi}',  (hx, hy, 0.48), 0.09, 0.15, MHyd, seg=8)
        bx(col, f'Hydrant_Bolt_{hi}', (hx, hy, 0.32), (0.24, 0.10, 0.10), MHyd)

    # Trash cans
    MGray = mk_mat('TrashCan', (0.28, 0.27, 0.26), rough=0.9)
    for ti in range(5):
        tx = 3.8; ty_ = -98 + ti * 12
        cy(col, f'Trash_{ti}', (tx, ty_, 0.35), 0.22, 0.65, MGray, seg=8)

    print("  ✓ Street details built")

# ─── World Setup ─────────────────────────────────────────────────────────────

def setup_world():
    world = bpy.data.worlds.new('NYCWorld')
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree; nt.nodes.clear()
    bg  = nt.nodes.new('ShaderNodeBackground')
    sky = nt.nodes.new('ShaderNodeTexSky')
    sky.sky_type        = 'HOSEK_WILKIE'
    sky.sun_elevation   = math.radians(16)  # golden hour
    sky.sun_rotation    = math.radians(195)
    sky.air_density     = 1.0
    sky.aerosol_density = 1.4  # slight haze
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg.inputs['Strength'].default_value = 1.05
    nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

def setup_lighting():
    # Golden hour sun
    bpy.ops.object.light_add(type='SUN', location=(80, -60, 80))
    sun = bpy.context.active_object; sun.name = 'NYCSun'
    sun.data.energy = 5.5; sun.data.color = (1.0, 0.91, 0.74)
    sun.rotation_euler = (math.radians(40), 0, math.radians(38))

    # Torch flame point light
    bpy.ops.object.light_add(type='POINT', location=(2.9, 0, 31.9))
    torch_light = bpy.context.active_object; torch_light.name = 'TorchLight'
    torch_light.data.energy = 600; torch_light.data.color = (1.0, 0.65, 0.1)
    torch_light.data.shadow_soft_size = 1.0

    # Water bounce fill
    bpy.ops.object.light_add(type='AREA', location=(0, 30, 2.0))
    fill = bpy.context.active_object; fill.name = 'WaterFill'
    fill.data.energy = 180; fill.data.color = (0.3, 0.55, 1.0)
    fill.data.size = 120; fill.rotation_euler = (math.radians(85), 0, 0)

    # City glow uplights
    for i, (lx_, ly_, c) in enumerate([
        (-25, -70, (1.0, 0.45, 0.12)),
        (25, -70,  (1.0, 0.50, 0.15)),
        (0,  -80,  (1.0, 0.48, 0.10)),
    ]):
        bpy.ops.object.light_add(type='POINT', location=(lx_, ly_, 2))
        l = bpy.context.active_object; l.name = f'CityGlow_{i}'
        l.data.energy = 600; l.data.color = c; l.data.shadow_soft_size = 8

def setup_camera():
    bpy.ops.object.camera_add(location=(-20, -130, 45))
    cam = bpy.context.active_object; cam.name = 'NYCCamera'
    cam.rotation_euler = (math.radians(60), 0, math.radians(-12))
    cam.data.lens = 28
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 135
    cam.data.dof.aperture_fstop = 5.6
    bpy.context.scene.camera = cam

def setup_render():
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.samples = 256; s.cycles.use_denoising = True
    s.render.resolution_x = 2560; s.render.resolution_y = 1440

    # Compositor bloom (Blender 5.x API)
    import bpy as _bpy
    nt = _bpy.data.node_groups.new('CompositorNodes', 'CompositorNodeTree')
    s.compositing_node_group = nt
    rn  = nt.nodes.new('CompositorNodeRLayers')
    gl  = nt.nodes.new('CompositorNodeGlare')
    vw  = nt.nodes.new('CompositorNodeViewer')
    nt.links.new(rn.outputs['Image'], gl.inputs['Image'])
    nt.links.new(gl.outputs['Image'], vw.inputs['Image'])

# ─── Run ─────────────────────────────────────────────────────────────────────

print("=" * 52)
print("  NYC Landmarks Builder — Biometric City")
print("=" * 52)

print("\n[1/7] Clearing scene...")
clear_scene()

print("[2/7] Building Statue of Liberty...")
build_sol(ox=0, oy=0)

print("[3/7] Building Brooklyn Bridge...")
build_brooklyn_bridge(bx_=10, by=30)

print("[4/7] Building harbor water...")
build_harbor()

print("[5/7] Building shoreline details...")
build_shoreline()

print("[6/7] Building NYC skyline background...")
build_skyline()

print("[7/7] Setting up world, lights, camera, render...")
build_street_details()
setup_world()
setup_lighting()
setup_camera()
setup_render()

# Frame all objects nicely
bpy.ops.object.select_all(action='SELECT')

print("\n✅ NYC scene complete!")
print("   Press NUMPAD 0 → camera view, Z → Rendered to preview")
print("   F12 to render (256 samples + denoising, ~2-5 min)")
