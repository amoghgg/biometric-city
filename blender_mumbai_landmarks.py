"""
Mumbai Landmarks for Biometric City
Builds: Taj Mahal Palace Hotel, Mumbai Chawls, Marine Drive, Gateway of India
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

# ─── Taj Mahal Palace Hotel ───────────────────────────────────────────────────
# Located at origin, faces the Arabian Sea (south = -Y direction)

def build_taj_hotel(ox=0, oy=0):
    col = bpy.data.collections.new('TajMahalPalace')
    bpy.context.scene.collection.children.link(col)

    # Colors — Indo-Saracenic architecture: warm sandstone, white stucco, copper domes
    MT   = mk_mat('Taj_Terra',   (0.82, 0.62, 0.44), rough=0.85)      # Warm terracotta/sandstone
    MW   = mk_mat('Taj_White',   (0.95, 0.93, 0.88), rough=0.80)      # White stucco
    MD   = mk_mat('Taj_Dome',    (0.30, 0.52, 0.38), rough=0.55, metal=0.2)  # Weathered copper dome
    MR   = mk_mat('Taj_Red',     (0.75, 0.35, 0.20), rough=0.82)      # Red sandstone accents
    MWin = mk_mat('Taj_Win',     (0.65, 0.85, 1.00), rough=0.05, metal=0.0,
                   emit=(0.8, 0.95, 1.0), emit_str=2.0)               # Warm lit windows
    MBal = mk_mat('Taj_Balcony', (0.88, 0.84, 0.76), rough=0.88)      # Balcony stone
    MRoof= mk_mat('Taj_Roof',    (0.55, 0.45, 0.32), rough=0.90)      # Clay roof tiles
    MArc = mk_mat('Taj_Arch',    (0.92, 0.90, 0.84), rough=0.82)      # Arch white stucco
    MFlag= mk_mat('Taj_Flag',    (0.0,  0.38, 0.80), rough=0.9)       # Indian blue flag

    # ── Central Tower Block (the iconic domed tower) ────────────────────────
    # Base plinth
    bx(col, 'T_Plinth',     (ox, oy, 0.6),      (12.0, 10.0, 1.2), MT)
    # Ground floor — wide main block
    bx(col, 'T_Ground',     (ox, oy, 3.5),      (11.0, 9.5,  5.5), MT)
    # First floor with slightly narrower face
    bx(col, 'T_Floor1',     (ox, oy, 8.0),      (10.5, 9.0,  3.5), MT)
    # Second floor
    bx(col, 'T_Floor2',     (ox, oy, 12.0),     (10.0, 8.5,  3.5), MT)
    # Third floor (white stucco transitions)
    bx(col, 'T_Floor3',     (ox, oy, 16.0),     (9.0,  8.0,  3.5), MW)
    # Parapet level
    bx(col, 'T_Parapet',    (ox, oy, 19.5),     (9.5,  8.5,  0.6), MT)
    # Octagonal base for dome
    bpy.ops.mesh.primitive_cylinder_add(radius=3.8, depth=2.0, vertices=8,
                                         location=(ox, oy, 21.5))
    oct_base = bpy.context.active_object; oct_base.name = 'T_OctBase'
    oct_base.data.materials.append(MW); lnk(col, oct_base)
    # Drum (cylindrical neck)
    cy(col, 'T_Drum',       (ox, oy, 23.8),     3.2, 2.5, MW, seg=16)
    # Main onion dome (sphere + cone combination)
    sp(col, 'T_DomeBody',   (ox, oy, 26.5),     3.0, MD, seg=20)
    # Dome neck (narrows and then flares)
    cy(col, 'T_DomeNeck',   (ox, oy, 25.2),     1.2, 1.0, MD, seg=12)
    cn(col, 'T_DomeFlare',  (ox, oy, 23.5),     2.5, 1.5, 2.0, MD, seg=16)
    # Finial
    cn(col, 'T_DomeFinial', (ox, oy, 29.2),     0.35, 0.04, 1.8, MD, seg=10)
    sp(col, 'T_FinialBall', (ox, oy, 30.2),     0.28, mk_mat('FinialGold', (0.9,0.75,0.2),
                                                               rough=0.1, metal=0.95), seg=8)

    # ── 4 Corner Turrets (octagonal towers with smaller domes) ──────────────
    turret_offsets = [(-4.5, -3.8), (4.5, -3.8), (-4.5, 3.8), (4.5, 3.8)]
    for ti, (tx, ty) in enumerate(turret_offsets):
        px, py = ox+tx, oy+ty
        # Turret shaft
        bpy.ops.mesh.primitive_cylinder_add(radius=1.4, depth=14, vertices=8,
                                             location=(px, py, 7.5))
        turr = bpy.context.active_object; turr.name = f'T_Turret_{ti}'
        turr.data.materials.append(MT if ti%2==0 else MW); lnk(col, turr)
        # Balcony ring at mid-height
        tr(col, f'T_TurretRing_{ti}', (px, py, 10.5), 1.6, 0.14, MArc)
        # Balcony overhang
        cy(col, f'T_TurretBalc_{ti}', (px, py, 10.8), 1.7, 0.25, MArc, seg=8)
        # Turret cap — octagonal parapet
        bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=1.0, vertices=8,
                                             location=(px, py, 15.2))
        cap = bpy.context.active_object; cap.name = f'T_TurretCap_{ti}'
        cap.data.materials.append(MW); lnk(col, cap)
        # Small dome
        sp(col, f'T_TurretDome_{ti}', (px, py, 16.8), 1.35, MD, seg=14)
        cn(col, f'T_TurretDomeNeck_{ti}', (px, py, 15.8), 1.0, 0.7, 1.0, MD, seg=10)
        cn(col, f'T_TurretFinial_{ti}', (px, py, 18.0), 0.2, 0.02, 1.0,
           mk_mat(f'TurretFin', (0.9, 0.75, 0.2), rough=0.1, metal=0.95), seg=8)

    # ── North Wing (Taj Mahal Tower wing, lower residential block) ───────────
    # North wing runs to the left (negative X)
    bx(col, 'NW_Base',    (ox-16, oy, 0.6),  (18.0, 9.0, 1.2), MT)
    bx(col, 'NW_Gnd',     (ox-16, oy, 3.5),  (17.5, 8.5, 5.5), MT)
    bx(col, 'NW_F1',      (ox-16, oy, 8.0),  (17.0, 8.0, 3.5), MT)
    bx(col, 'NW_F2',      (ox-16, oy, 12.0), (16.5, 7.5, 3.5), MT)
    bx(col, 'NW_F3',      (ox-16, oy, 15.8), (16.0, 7.5, 3.0), MW)
    bx(col, 'NW_Parapet', (ox-16, oy, 17.8), (17.0, 8.0, 0.5), MT)
    # Saw-tooth roofline with small pointed turrets
    for j in range(5):
        px2 = ox - 8 - j*2
        cn(col, f'NW_Turret_{j}', (px2, oy+3.8, 18.8), 0.55, 0.04, 1.5, MD, seg=8)
        cn(col, f'NW_Turret_S{j}', (px2, oy-3.8, 18.8), 0.55, 0.04, 1.5, MD, seg=8)

    # ── South Wing (facing sea, has the famous arched colonnade) ─────────────
    bx(col, 'SW_Base',    (ox+18, oy, 0.6),  (22.0, 9.0, 1.2), MT)
    bx(col, 'SW_Gnd',     (ox+18, oy, 3.5),  (21.5, 8.5, 5.5), MT)
    bx(col, 'SW_F1',      (ox+18, oy, 8.0),  (21.0, 8.0, 3.5), MT)
    bx(col, 'SW_F2',      (ox+18, oy, 12.0), (20.5, 7.5, 3.5), MT)
    bx(col, 'SW_F3',      (ox+18, oy, 15.8), (20.0, 7.5, 3.0), MW)
    bx(col, 'SW_Parapet', (ox+18, oy, 17.8), (21.0, 8.0, 0.5), MT)

    # ── Arched colonnade on sea-facing (south) facade ──────────────────────
    # Pointed arches running along south face at ground level
    for ai in range(9):
        ax_ = ox - 18 + ai * 4.5
        # Arch pillar columns
        cy(col, f'Arch_Pillar_{ai}', (ax_, oy-4.8, 3.0), 0.25, 5.5, MArc, seg=8)
        # Arch frame (top curved approximated with cylinder flattened)
        bx(col, f'Arch_Spandrel_{ai}', (ax_, oy-4.8, 6.2), (0.5, 0.3, 0.6), MArc)

    # Arch lintels
    for ai in range(8):
        ax_ = ox - 15.75 + ai * 4.5
        bx(col, f'Arch_Lintel_{ai}', (ax_, oy-4.8, 6.5), (3.8, 0.25, 0.45), MArc)
        # Pointed arch apex
        cn(col, f'Arch_Apex_{ai}', (ax_, oy-4.85, 7.2), 0.6, 0.04, 1.0, MArc, seg=6)

    # ── Windows (rows across all floors) ───────────────────────────────────
    window_z = [4.2, 7.8, 12.0, 15.8]
    for fz in window_z:
        # Windows on main block north face
        for wi in range(-4, 5):
            bx(col, f'Win_N_{fz}_{wi}', (ox + wi*2.2, oy+4.85, fz), (0.9, 0.08, 1.1), MWin)
        # Windows on south face
        for wi in range(-4, 5):
            bx(col, f'Win_S_{fz}_{wi}', (ox + wi*2.2, oy-4.85, fz), (0.9, 0.08, 1.1), MWin)

    # Windows on north wing
    for fz in [4.2, 7.8, 12.0]:
        for wi in range(-11, 0):
            bx(col, f'Win_NW_{fz}_{wi}', (ox-8 + wi*1.6, oy+4.3, fz), (0.75, 0.08, 0.95), MWin)

    # ── Horizontal floor bands / string courses ─────────────────────────────
    for bz in [1.2, 6.8, 11.0, 14.5, 17.5]:
        # Central block
        bx(col, f'SC_C_{bz}', (ox, oy, bz), (11.8, 10.0, 0.18), MT)
        # North wing
        bx(col, f'SC_N_{bz}', (ox-16, oy, bz), (18.0, 9.0, 0.18), MT)
        # South wing
        bx(col, f'SC_S_{bz}', (ox+18, oy, bz), (22.0, 9.0, 0.18), MT)

    # ── Decorative chhajjas (horizontal sunshades) on each floor ───────────
    chhajja_z = [6.1, 10.6, 14.8]
    for cz in chhajja_z:
        # Main block
        bx(col, f'Chh_F_{cz}', (ox, oy-4.95, cz), (11.5, 0.9, 0.12), MBal)
        bx(col, f'Chh_B_{cz}', (ox, oy+4.95, cz), (11.5, 0.9, 0.12), MBal)
        # North wing
        bx(col, f'Chh_NW_{cz}', (ox-16, oy+4.35, cz), (18.0, 0.9, 0.12), MBal)

    # ── Roof Terrace ornaments ─────────────────────────────────────────────
    # Flag masts
    for fx in [ox-3, ox, ox+3]:
        cy(col, f'Flagpole_{fx}', (fx, oy, 21.2), 0.07, 4.0,
           mk_mat('Flagpole', (0.8, 0.75, 0.65), rough=0.5, metal=0.7), seg=6)
        bx(col, f'Flag_{fx}', (fx+0.7, oy, 22.8), (1.2, 0.04, 0.65), MFlag)

    # ── Entrance portico ──────────────────────────────────────────────────
    bx(col, 'Portico_Left',  (ox-3.0, oy-5.8, 4.0),  (1.5, 1.5, 7.0), MArc)
    bx(col, 'Portico_Right', (ox+3.0, oy-5.8, 4.0),  (1.5, 1.5, 7.0), MArc)
    bx(col, 'Portico_Top',   (ox,     oy-5.6, 7.8),  (7.5, 1.0, 0.5), MArc)
    # Entrance arch
    cn(col, 'Portico_Arch',  (ox, oy-5.7, 8.5),       1.5, 0.1, 1.8, MArc, seg=12)

    # Entrance driveway
    bx(col, 'Driveway', (ox, oy-8, -0.1), (10.0, 5.0, 0.2),
       mk_mat('Driveway', (0.35, 0.32, 0.28), rough=0.85))

    # ── Garden / courtyard ────────────────────────────────────────────────
    MG = mk_mat('Garden', (0.12, 0.38, 0.10), rough=0.95)
    MGravel = mk_mat('Garden_Path', (0.55, 0.50, 0.42), rough=0.9)
    bx(col, 'Garden_Main', (ox-8, oy-12, -0.1), (12.0, 8.0, 0.2), MG)
    bx(col, 'Garden_Path1', (ox, oy-10, 0.01), (1.2, 10.0, 0.12), MGravel)
    bx(col, 'Garden_Path2', (ox-8, oy-12, 0.01), (10.0, 1.2, 0.12), MGravel)

    # Palm trees in garden
    MTrunk = mk_mat('Palm_Trunk', (0.55, 0.42, 0.28), rough=0.9)
    MLeaf  = mk_mat('Palm_Leaf',  (0.18, 0.55, 0.15), rough=0.88)
    for pi, (ptx, pty) in enumerate([(-12, -9), (-4, -9), (-12, -15), (-4, -15)]):
        px_, py_ = ox+ptx, oy+pty
        cy(col, f'Palm_Trunk_{pi}', (px_, py_, 3.0), 0.22, 5.5, MTrunk, seg=8)
        # Leaf crown
        for li in range(6):
            angle = li / 6 * math.pi * 2
            lx_ = px_ + math.cos(angle) * 1.8
            ly_ = py_ + math.sin(angle) * 1.8
            cn(col, f'Palm_Leaf_{pi}_{li}', (lx_, ly_, 5.5), 0.12, 0.02, 2.2, MLeaf,
               rot=(math.radians(35)*math.cos(angle), math.radians(35)*math.sin(angle), 0), seg=5)
        sp(col, f'Palm_Crown_{pi}', (px_, py_, 5.9), 0.55, MLeaf, seg=8)

    print(f"  ✓ Taj Mahal Palace Hotel built at ({ox:.0f}, {oy:.0f}), height ~{31.0:.1f} units")

# ─── Mumbai Chawl ─────────────────────────────────────────────────────────────
# Traditional Mumbai tenement buildings with shared corridors

def build_mumbai_chawl(ox=0, oy=0, floors=4, width=12.0, depth=8.0, name_prefix='Chawl'):
    col = bpy.data.collections.new(name_prefix)
    bpy.context.scene.collection.children.link(col)

    # Chawl materials — weathered, aged concrete and brick
    MC   = mk_mat(f'{name_prefix}_Concrete', (0.58, 0.54, 0.48), rough=0.92)
    MCW  = mk_mat(f'{name_prefix}_WeathWall', (0.52, 0.48, 0.42), rough=0.94)
    MBr  = mk_mat(f'{name_prefix}_Brick',    (0.68, 0.48, 0.35), rough=0.90)
    MBal = mk_mat(f'{name_prefix}_Balcony',  (0.45, 0.43, 0.40), rough=0.88)
    MRst = mk_mat(f'{name_prefix}_Rust',     (0.65, 0.35, 0.15), rough=0.94)   # rust stains
    MWin = mk_mat(f'{name_prefix}_Win',      (0.55, 0.75, 0.95), rough=0.08, metal=0.0,
                   emit=(0.8, 0.85, 0.6), emit_str=1.8)                         # warm window glow
    MDoor= mk_mat(f'{name_prefix}_Door',     (0.28, 0.18, 0.10), rough=0.85)   # dark wood doors
    MWater= mk_mat(f'{name_prefix}_WaterTank',(0.35, 0.38, 0.42), rough=0.75, metal=0.3)
    MAC   = mk_mat(f'{name_prefix}_AC',      (0.50, 0.52, 0.54), rough=0.6, metal=0.5)
    MBar  = mk_mat(f'{name_prefix}_Rail',    (0.22, 0.20, 0.18), rough=0.75, metal=0.3)
    MLaundry = mk_mat(f'{name_prefix}_Laundry', (0.85, 0.72, 0.60), rough=0.92)

    floor_h = 3.2
    total_h  = floors * floor_h

    # Foundation slab
    bx(col, f'{name_prefix}_Foundation', (ox, oy, 0.3), (width+0.5, depth+0.5, 0.6), MC)

    # Main building body
    bx(col, f'{name_prefix}_Body', (ox, oy, total_h/2 + 0.6),
       (width, depth, total_h), MCW)

    # Stairwell / staircase tower (one side)
    stair_x = ox + width/2 + 0.8
    cy(col, f'{name_prefix}_StairTower', (stair_x, oy, total_h/2 + 0.6), 1.5, total_h, MC, seg=8)
    # Stairwell windows
    for sf in range(floors):
        sz = 0.6 + sf * floor_h + floor_h/2
        bx(col, f'{name_prefix}_StairWin_{sf}', (stair_x + 1.4, oy, sz), (0.08, 0.7, 0.8), MWin)

    # ── Per-floor corridor / balcony on front face (south = -y) ────────────
    for f in range(floors):
        fz = 0.6 + f * floor_h
        # Floor slab at front (balcony/corridor)
        bx(col, f'{name_prefix}_Balcony_{f}', (ox, oy - depth/2 - 0.6, fz + floor_h - 0.2),
           (width + 0.4, 1.2, 0.22), MBal)
        # Balcony railing (iron bars)
        for ri in range(int(width)):
            bar_x = ox - width/2 + ri + 0.5
            cy(col, f'{name_prefix}_Bar_{f}_{ri}',
               (bar_x, oy - depth/2 - 1.0, fz + floor_h + 0.4),
               0.035, 0.75, MBar, seg=5)
        # Railing top rail
        bx(col, f'{name_prefix}_RailTop_{f}',
           (ox, oy - depth/2 - 1.0, fz + floor_h + 0.85),
           (width + 0.2, 0.06, 0.07), MBar)

        # Windows + doors on each unit (typically ~3m wide units)
        units = max(2, int(width / 3.5))
        unit_w = width / units
        for u in range(units):
            ux = ox - width/2 + (u + 0.5) * unit_w
            uf = oy - depth/2 - 0.02
            # Door (ground floor) or window (upper floors)
            if f == 0:
                bx(col, f'{name_prefix}_Door_{u}', (ux, uf, fz + 1.2), (1.0, 0.09, 2.0), MDoor)
                # Door frame
                bx(col, f'{name_prefix}_DFrame_L{u}', (ux-0.55, uf, fz+1.2), (0.08, 0.1, 2.2), MCW)
                bx(col, f'{name_prefix}_DFrame_R{u}', (ux+0.55, uf, fz+1.2), (0.08, 0.1, 2.2), MCW)
                bx(col, f'{name_prefix}_DFrame_T{u}', (ux, uf, fz+2.3), (1.3, 0.1, 0.15), MCW)
            else:
                # Window
                bx(col, f'{name_prefix}_Win_{f}_{u}', (ux, uf, fz + 1.6), (0.9, 0.09, 1.1), MWin)
                # Window grilles (thin horizontal bars)
                for gi in range(3):
                    bx(col, f'{name_prefix}_Grille_{f}_{u}_{gi}',
                       (ux, uf, fz + 1.2 + gi*0.35), (0.92, 0.07, 0.04), MBar)

        # AC units hanging from windows (upper floors, random placement)
        if f > 0:
            random.seed(hash(name_prefix + str(f)) % 9999)
            for u in range(units):
                if random.random() > 0.4:
                    ux = ox - width/2 + (u + 0.5) * unit_w
                    bx(col, f'{name_prefix}_AC_{f}_{u}',
                       (ux + random.uniform(-0.3, 0.3), oy - depth/2 - 0.25, fz + 1.1),
                       (0.7, 0.3, 0.5), MAC)

    # ── Laundry lines strung across the front ───────────────────────────────
    for f in range(1, floors):
        fz = 0.6 + f * floor_h + floor_h - 0.4
        # Wire (thin cylinder)
        bx(col, f'{name_prefix}_Wire_{f}', (ox, oy - depth/2 - 0.8, fz),
           (width - 1.0, 0.025, 0.025), MBar)
        # Clothes hanging (flat rectangles at intervals)
        random.seed(hash(name_prefix + 'laundry' + str(f)) % 9999)
        num_clothes = random.randint(3, 7)
        for ci in range(num_clothes):
            cx_ = ox - width/2 + 1.0 + ci * (width-2.0) / num_clothes
            cw = random.uniform(0.5, 1.0)
            ch = random.uniform(0.6, 1.0)
            # Slightly varied colors — whites, blues, reds
            r_ = random.uniform(0.4, 1.0)
            g_ = random.uniform(0.4, 0.9)
            b_ = random.uniform(0.4, 1.0)
            bx(col, f'{name_prefix}_Cloth_{f}_{ci}',
               (cx_, oy - depth/2 - 0.78, fz - ch/2 - 0.1),
               (cw, 0.03, ch),
               mk_mat(f'{name_prefix}_Cloth_{f}_{ci}', (r_, g_, b_), rough=0.95))

    # ── Rooftop elements ────────────────────────────────────────────────────
    roof_z = total_h + 0.6
    # Parapet
    bx(col, f'{name_prefix}_ParapetF', (ox, oy - depth/2, roof_z + 0.5),
       (width + 0.3, 0.3, 0.9), MBal)
    bx(col, f'{name_prefix}_ParapetB', (ox, oy + depth/2, roof_z + 0.5),
       (width + 0.3, 0.3, 0.9), MBal)
    for side in [-1, 1]:
        bx(col, f'{name_prefix}_ParapetS_{side}',
           (ox + side*(width/2), oy, roof_z + 0.5),
           (0.3, depth + 0.3, 0.9), MBal)

    # Water tank
    cy(col, f'{name_prefix}_WaterTank', (ox + width/4, oy - depth/4, roof_z + 0.9),
       1.2, 1.6, MWater, seg=10)
    cn(col, f'{name_prefix}_TankLid',   (ox + width/4, oy - depth/4, roof_z + 1.9),
       1.3, 0.05, 0.4, MWater, seg=10)
    # Tank support legs
    for li in range(3):
        angle = li / 3 * math.pi * 2
        lx_ = ox + width/4 + math.cos(angle) * 0.9
        ly_ = oy - depth/4 + math.sin(angle) * 0.9
        cy(col, f'{name_prefix}_TankLeg_{li}', (lx_, ly_, roof_z + 0.3), 0.08, 0.6,
           mk_mat('TankLeg', (0.3, 0.28, 0.25), rough=0.85), seg=5)

    # Satellite dishes
    for di in range(2):
        dx_ = ox - width/4 + di * width/2
        bx(col, f'{name_prefix}_Dish_{di}', (dx_, oy + depth/4, roof_z + 0.8),
           (0.6, 0.04, 0.5), mk_mat('Dish', (0.65, 0.62, 0.58), rough=0.7, metal=0.4),
           rot=(math.radians(-20), 0, 0))

    # Roof solar water heater (common in Mumbai)
    bx(col, f'{name_prefix}_SolarHeater',
       (ox - width/4, oy, roof_z + 0.6),
       (2.0, 0.8, 0.15),
       mk_mat(f'{name_prefix}_Solar', (0.06, 0.06, 0.10), rough=0.2, metal=0.6),
       rot=(math.radians(-15), 0, 0))

    # Rust stain marks on facade (thin darker vertical strips)
    random.seed(hash(name_prefix + 'rust') % 9999)
    for ri in range(4):
        rx_ = ox - width/2 + random.uniform(1, width-1)
        rz_ = random.uniform(2, total_h - 2)
        rh_ = random.uniform(2, 6)
        bx(col, f'{name_prefix}_RustStain_{ri}', (rx_, oy - depth/2, rz_),
           (0.12, 0.02, rh_), MRst)

    print(f"  ✓ {name_prefix} built ({floors} floors, {width:.0f}m wide)")

# ─── Gateway of India ─────────────────────────────────────────────────────────

def build_gateway_of_india(ox=0, oy=0):
    col = bpy.data.collections.new('GatewayOfIndia')
    bpy.context.scene.collection.children.link(col)

    MB  = mk_mat('GOI_Basalt',  (0.42, 0.38, 0.32), rough=0.88)   # yellow basalt
    MBY = mk_mat('GOI_Yellow',  (0.85, 0.75, 0.50), rough=0.85)   # warm honey stone
    MA  = mk_mat('GOI_Arch',    (0.90, 0.82, 0.65), rough=0.82)   # lighter arch stone

    # Base plinth
    bx(col, 'GOI_Plinth', (ox, oy, 0.8), (20.0, 12.0, 1.5), MB)
    # Lower block
    bx(col, 'GOI_Base',   (ox, oy, 3.0), (18.0, 10.0, 3.0), MBY)

    # ── Two flanking towers ──────────────────────────────────────────────────
    for tx, side in [(-7.0, 'L'), (7.0, 'R')]:
        # Tower shaft
        bpy.ops.mesh.primitive_cylinder_add(radius=2.8, depth=14, vertices=8,
                                             location=(ox+tx, oy, 10))
        tower = bpy.context.active_object; tower.name = f'GOI_Tower_{side}'
        tower.data.materials.append(MBY); lnk(col, tower)
        # Tower mid band
        bx(col, f'GOI_Band_{side}', (ox+tx, oy, 10), (6.5, 6.5, 0.4), MB)
        # Tower dome
        sp(col, f'GOI_TowerDome_{side}', (ox+tx, oy, 17.5), 2.6,
           mk_mat(f'GOI_Dome', (0.38, 0.55, 0.42), rough=0.6, metal=0.2), seg=16)
        # Tower finial
        cn(col, f'GOI_TowerFinial_{side}', (ox+tx, oy, 20.0),
           0.3, 0.02, 1.5, MB, seg=8)

    # ── Central arch (tall pointed Mughal arch) ──────────────────────────────
    # Arch void cut-out is approximated by arch frame pieces
    bx(col, 'GOI_ArchL',  (ox-2.5, oy, 8.0), (1.5, 10.1, 10.0), MBY)  # left jamb
    bx(col, 'GOI_ArchR',  (ox+2.5, oy, 8.0), (1.5, 10.1, 10.0), MBY)  # right jamb
    bx(col, 'GOI_ArchTop',(ox, oy, 13.5), (5.0, 10.1, 1.5), MBY)       # spandrel
    # Pointed keystone
    cn(col, 'GOI_Keystone', (ox, oy, 14.8), 1.2, 0.1, 1.8, MA, seg=8)

    # Passage opening (dark void)
    bx(col, 'GOI_Passage', (ox, oy, 6.5), (4.0, 10.2, 10.5),
       mk_mat('GOI_Void', (0.03, 0.03, 0.03), rough=0.98))

    # ── Decorative lattice panels ────────────────────────────────────────────
    for side_y, name_s in [(-5.0, 'F'), (5.0, 'B')]:
        for li in range(4):
            lx_ = ox - 5.5 + li * 3.8
            bx(col, f'GOI_Lattice_{name_s}_{li}',
               (lx_, oy+side_y, 6.0), (1.2, 0.15, 7.0), MA)
            # Lattice horizontal bars
            for lz in range(4):
                bx(col, f'GOI_LatBar_{name_s}_{li}_{lz}',
                   (lx_, oy+side_y, 3.5 + lz*1.6), (1.25, 0.12, 0.12), MA)

    # ── Water steps (descending into the sea) ────────────────────────────────
    MStep = mk_mat('GOI_Step', (0.48, 0.44, 0.38), rough=0.88)
    for si in range(5):
        step_w = 22.0 + si * 1.5
        bx(col, f'GOI_Step_{si}', (ox, oy-7.5-si*1.8, -si*0.4), (step_w, 2.0, 0.4), MStep)

    # Promenade / plaza
    bx(col, 'GOI_Plaza', (ox, oy+4, -0.2), (40.0, 16.0, 0.25),
       mk_mat('GOI_Plaza', (0.60, 0.56, 0.48), rough=0.88))

    # Plaza lamp posts
    MLP = mk_mat('GOI_Lamp', (0.22, 0.20, 0.18), rough=0.7, metal=0.5)
    MLG = mk_mat('GOI_LampGlow', (1.0, 0.95, 0.7), rough=0.2,
                  emit=(1.0, 0.95, 0.7), emit_str=8.0)
    for li in range(6):
        lx_ = ox - 18 + li * 7.5
        cy(col, f'GOI_Lamp_{li}', (lx_, oy+8, 2.0), 0.1, 4.0, MLP, seg=6)
        sp(col, f'GOI_LampGlobe_{li}', (lx_, oy+8, 4.2), 0.25, MLG, seg=6)

    print(f"  ✓ Gateway of India built at ({ox:.0f}, {oy:.0f})")

# ─── Marine Drive (Queen's Necklace) ─────────────────────────────────────────

def build_marine_drive(ox=0, oy=0):
    col = bpy.data.collections.new('MarineDrive')
    bpy.context.scene.collection.children.link(col)

    MRd = mk_mat('MD_Road',      (0.12, 0.11, 0.12), rough=0.88)
    MPav= mk_mat('MD_Pavement',  (0.55, 0.52, 0.46), rough=0.90)
    MSea= mk_mat('MD_Sea',       (0.03, 0.10, 0.20), rough=0.06,
                  emit=(0.02, 0.06, 0.14), emit_str=0.5)
    MWall= mk_mat('MD_SeaWall',  (0.45, 0.42, 0.38), rough=0.88)

    # Curved drive — approximated as straight stretch + curve using segments
    DRIVE_LEN = 120.0
    CURVE_SEGS = 20
    for si in range(CURVE_SEGS):
        # Follow a gentle curve
        t = si / CURVE_SEGS
        angle = t * math.radians(60)  # 60 degree arc
        seg_x = ox + math.sin(angle) * 60
        seg_y = oy - math.cos(angle) * 60 + 60
        bx(col, f'MD_Road_{si}', (seg_x, seg_y, -0.05), (10.0, DRIVE_LEN/CURVE_SEGS + 0.5, 0.3), MRd,
           rot=(0, 0, angle))
        bx(col, f'MD_Pav_{si}',  (seg_x + math.cos(angle)*7, seg_y + math.sin(angle)*7, -0.05),
           (4.0, DRIVE_LEN/CURVE_SEGS + 0.5, 0.28), MPav, rot=(0, 0, angle))

    # Sea promenade wall
    for si in range(CURVE_SEGS):
        t = si / CURVE_SEGS
        angle = t * math.radians(60)
        seg_x = ox + math.sin(angle) * 52
        seg_y = oy - math.cos(angle) * 52 + 60
        bx(col, f'MD_Wall_{si}', (seg_x + math.cos(angle)*4, seg_y + math.sin(angle)*4, 0.5),
           (0.5, DRIVE_LEN/CURVE_SEGS + 0.5, 1.0), MWall, rot=(0, 0, angle))

    # Sea water beyond the wall
    bpy.ops.mesh.primitive_plane_add(size=200, location=(ox-60, oy, -0.6))
    sea = bpy.context.active_object; sea.name = 'ArabianSea'
    sea.data.materials.append(MSea)
    mod = sea.modifiers.new('SeaWave', 'WAVE')
    mod.height = 0.3; mod.width = 3.0; mod.speed = 0.3
    lnk(col, sea)

    # Street lights along the drive (the famous necklace pattern)
    MLG = mk_mat('MD_LampGlow', (1.0, 0.90, 0.5), rough=0.2,
                  emit=(1.0, 0.90, 0.5), emit_str=10.0)
    MLP = mk_mat('MD_LampPole', (0.22, 0.20, 0.22), rough=0.7, metal=0.6)
    for si in range(0, CURVE_SEGS, 2):
        t = si / CURVE_SEGS
        angle = t * math.radians(60)
        lx_ = ox + math.sin(angle) * 56
        ly_ = oy - math.cos(angle) * 56 + 60
        cy(col, f'MD_Lamp_{si}', (lx_, ly_, 2.0), 0.07, 4.5, MLP, seg=6)
        sp(col, f'MD_LampGlobe_{si}', (lx_, ly_, 4.5), 0.22, MLG, seg=6)

    print(f"  ✓ Marine Drive built at ({ox:.0f}, {oy:.0f})")

# ─── Mumbai Skyline background ────────────────────────────────────────────────

def build_mumbai_skyline(ox=0, oy=0):
    col = bpy.data.collections.new('MumbaiSkyline')
    bpy.context.scene.collection.children.link(col)

    # Mumbai colors: terracotta, warm concrete, some glass
    mats = [
        mk_mat('Mum_Terra',  (0.78, 0.55, 0.35), rough=0.88,
               emit=(1.0, 0.75, 0.4), emit_str=1.5),
        mk_mat('Mum_Conc',   (0.62, 0.58, 0.50), rough=0.90,
               emit=(1.0, 0.85, 0.55), emit_str=1.2),
        mk_mat('Mum_Glass',  (0.20, 0.38, 0.60), rough=0.08, metal=0.75,
               emit=(0.4, 0.7, 1.0), emit_str=2.0),
        mk_mat('Mum_Cream',  (0.90, 0.84, 0.70), rough=0.85,
               emit=(1.0, 0.88, 0.62), emit_str=1.3),
    ]

    random.seed(88)
    # Background residential blocks (BKC, Nariman Point direction)
    for i in range(70):
        bx_ = ox + random.uniform(-80, 80)
        by_ = oy + random.uniform(30, 90)
        w = random.uniform(3.0, 8.0); d = random.uniform(3.0, 7.0)
        h = random.uniform(8, 30)
        m = random.choice(mats)
        bpy.ops.mesh.primitive_cube_add(location=(bx_, by_, h/2))
        o = bpy.context.active_object; o.scale = (w, d, h)
        bpy.ops.object.transform_apply(scale=True)
        o.data.materials.append(m); lnk(col, o)

        # Roof water tower (very common in Mumbai)
        if random.random() > 0.5 and h > 10:
            cy(col, f'Mum_WT_{i}', (bx_+random.uniform(-1,1), by_+random.uniform(-1,1), h+0.4),
               0.55, 1.2, m, seg=10)
            cn(col, f'Mum_WTCap_{i}', (bx_+random.uniform(-1,1), by_+random.uniform(-1,1), h+1.2),
               0.6, 0.02, 0.5, mk_mat(f'WTCap', (0.05,0.05,0.05), rough=0.9), seg=10)

    print(f"  ✓ Mumbai skyline built")

# ─── World and Lighting ───────────────────────────────────────────────────────

def setup_world():
    world = bpy.data.worlds.new('MumbaiWorld')
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree; nt.nodes.clear()
    bg  = nt.nodes.new('ShaderNodeBackground')
    sky = nt.nodes.new('ShaderNodeTexSky')
    sky.sky_type        = 'HOSEK_WILKIE'
    sky.sun_elevation   = math.radians(22)    # slightly higher sun — tropical
    sky.sun_rotation    = math.radians(180)
    sky.air_density     = 1.0
    sky.aerosol_density = 2.0    # more haze for Mumbai humidity
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg.inputs['Strength'].default_value = 1.2
    nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

def setup_lighting():
    # Hot Mumbai sun
    bpy.ops.object.light_add(type='SUN', location=(60, -60, 90))
    sun = bpy.context.active_object; sun.name = 'MumbaiSun'
    sun.data.energy = 6.0; sun.data.color = (1.0, 0.92, 0.72)
    sun.rotation_euler = (math.radians(45), 0, math.radians(30))

    # Sea bounce (warm teal reflection)
    bpy.ops.object.light_add(type='AREA', location=(0, -50, 2))
    sea_fill = bpy.context.active_object; sea_fill.name = 'SeaBounce'
    sea_fill.data.energy = 200; sea_fill.data.color = (0.4, 0.7, 0.8)
    sea_fill.data.size = 80; sea_fill.rotation_euler = (math.radians(80), 0, 0)

    # Warm ambient for twilight
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 80))
    sky_fill = bpy.context.active_object; sky_fill.name = 'SkyFill'
    sky_fill.data.energy = 120; sky_fill.data.color = (1.0, 0.82, 0.60)
    sky_fill.data.size = 120

def setup_camera():
    bpy.ops.object.camera_add(location=(-80, -80, 50))
    cam = bpy.context.active_object; cam.name = 'MumbaiCamera'
    # Point at Taj hotel
    target = Vector((0, 0, 15))
    direction = target - cam.location
    rot = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot.to_euler()
    cam.data.lens = 28
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 110
    cam.data.dof.aperture_fstop = 5.6
    bpy.context.scene.camera = cam

def setup_render():
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 256; sc.cycles.use_denoising = True
    sc.render.resolution_x = 2560; sc.render.resolution_y = 1440
    nt = bpy.data.node_groups.new('MumbaiComp', 'CompositorNodeTree')
    sc.compositing_node_group = nt
    rn = nt.nodes.new('CompositorNodeRLayers')
    gl = nt.nodes.new('CompositorNodeGlare')
    vw = nt.nodes.new('CompositorNodeViewer')
    nt.links.new(rn.outputs['Image'], gl.inputs['Image'])
    nt.links.new(gl.outputs['Image'], vw.inputs['Image'])

# ─── Run ─────────────────────────────────────────────────────────────────────

print("=" * 52)
print("  Mumbai Landmarks Builder — Biometric City")
print("=" * 52)

print("\n[1/8] Clearing scene...")
clear_scene()

print("[2/8] Building Taj Mahal Palace Hotel...")
build_taj_hotel(ox=0, oy=0)

print("[3/8] Building Mumbai chawl #1 (4-floor)...")
build_mumbai_chawl(ox=-30, oy=10, floors=4, width=12.0, name_prefix='Chawl_A')

print("[4/8] Building Mumbai chawl #2 (5-floor, wider)...")
build_mumbai_chawl(ox=-45, oy=-5, floors=5, width=15.0, name_prefix='Chawl_B')

print("[5/8] Building Mumbai chawl #3 (3-floor narrow)...")
build_mumbai_chawl(ox=-30, oy=30, floors=3, width=8.5, name_prefix='Chawl_C')

print("[6/8] Building Gateway of India...")
build_gateway_of_india(ox=30, oy=-20)

print("[7/8] Building Marine Drive...")
build_marine_drive(ox=0, oy=-50)

print("[8/8] Building Mumbai skyline background...")
build_mumbai_skyline(ox=0, oy=0)

print("Setting up world, lights, camera, render...")
setup_world()
setup_lighting()
setup_camera()
setup_render()

bpy.ops.object.select_all(action='SELECT')

print("\n✅ Mumbai scene complete!")
print("   Press NUMPAD 0 → camera view, Z → Rendered to preview")
print("   F12 to render (256 samples + denoising)")
