"""
NYC Detailed Scene — Biometric City
Geographically accurate placement with detailed buildings, harbor, and landmarks.
Coordinate system: 1 unit ≈ 30m, Battery Park at origin, Y = uptown, X = east
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

def mk(name, color, rough=0.8, metal=0.0, emit=None, es=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (*color, 1)
        b.inputs['Roughness'].default_value = rough
        b.inputs['Metallic'].default_value = metal
        if emit and es > 0:
            b.inputs['Emission Color'].default_value = (*emit, 1)
            b.inputs['Emission Strength'].default_value = es
    return m

def L(col, obj):
    for c in obj.users_collection: c.objects.unlink(obj)
    col.objects.link(obj)
    return obj

def B(col, n, loc, sc, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = n
    o.scale = sc; o.rotation_euler = rot
    bpy.ops.object.transform_apply(scale=True, rotation=any(r!=0 for r in rot))
    o.data.materials.append(mat); return L(col, o)

def C(col, n, loc, r, h, mat, rot=(0,0,0), seg=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=seg, location=loc)
    o = bpy.context.active_object; o.name = n
    if any(r_!=0 for r_ in rot):
        o.rotation_euler = rot; bpy.ops.object.transform_apply(rotation=True)
    o.data.materials.append(mat); return L(col, o)

def K(col, n, loc, r1, r2, h, mat, rot=(0,0,0), seg=12):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=h, vertices=seg, location=loc)
    o = bpy.context.active_object; o.name = n
    if any(r_!=0 for r_ in rot):
        o.rotation_euler = rot; bpy.ops.object.transform_apply(rotation=True)
    o.data.materials.append(mat); return L(col, o)

def S(col, n, loc, r, mat, seg=12):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=8)
    o = bpy.context.active_object; o.name = n
    o.data.materials.append(mat); return L(col, o)

# ─── Material Library ─────────────────────────────────────────────────────────

class Mats:
    pass

def init_mats():
    m = Mats()
    # Building facades
    m.glass_blue   = mk('Glass_Blue',   (0.18, 0.35, 0.58), rough=0.06, metal=0.80, emit=(0.4,0.65,1.0), es=2.0)
    m.glass_dark   = mk('Glass_Dark',   (0.10, 0.15, 0.25), rough=0.04, metal=0.85, emit=(0.3,0.55,0.9), es=2.5)
    m.glass_teal   = mk('Glass_Teal',   (0.15, 0.40, 0.50), rough=0.06, metal=0.78, emit=(0.4,0.8,0.9), es=1.8)
    m.brick_red    = mk('Brick_Red',    (0.65, 0.32, 0.18), rough=0.90, emit=(1,0.82,0.45), es=0.8)
    m.brick_brown  = mk('Brick_Brown',  (0.55, 0.38, 0.22), rough=0.88, emit=(1,0.85,0.5), es=0.7)
    m.limestone    = mk('Limestone',    (0.82, 0.78, 0.65), rough=0.84, emit=(1,0.9,0.6), es=1.0)
    m.concrete     = mk('Concrete',     (0.55, 0.52, 0.48), rough=0.88, emit=(0.9,0.8,0.55), es=0.6)
    m.art_deco     = mk('ArtDeco',      (0.72, 0.68, 0.56), rough=0.82, emit=(1,0.92,0.65), es=1.2)
    # Window frames
    m.win_frame    = mk('WinFrame',     (0.20, 0.22, 0.25), rough=0.70, metal=0.4)
    m.win_dark     = mk('WinDark',      (0.08, 0.12, 0.22), rough=0.15, emit=(0.5,0.7,1.0), es=1.5)
    # Environment
    m.asphalt      = mk('Asphalt',      (0.08, 0.08, 0.10), rough=0.88)
    m.sidewalk     = mk('Sidewalk',     (0.42, 0.40, 0.37), rough=0.90)
    m.water        = mk('Water',        (0.01, 0.04, 0.10), rough=0.03, emit=(0.02,0.05,0.12), es=0.4)
    m.park_grass   = mk('Grass',        (0.10, 0.35, 0.08), rough=0.95)
    m.tree_trunk   = mk('TreeTrunk',    (0.30, 0.22, 0.12), rough=0.92)
    m.tree_leaf    = mk('TreeLeaf',     (0.12, 0.42, 0.10), rough=0.90)
    m.verdigris    = mk('Verdigris',    (0.18, 0.47, 0.38), rough=0.62, metal=0.25)
    m.granite      = mk('Granite',      (0.50, 0.47, 0.43), rough=0.88)
    m.bridge_stone = mk('BridgeStone',  (0.70, 0.65, 0.56), rough=0.88)
    m.bridge_cable = mk('BridgeCable',  (0.28, 0.30, 0.32), rough=0.60, metal=0.8)
    m.road_line    = mk('YellowLine',   (0.9,0.85,0.1), rough=0.85, emit=(0.9,0.85,0.1), es=0.4)
    m.lamp_pole    = mk('LampPole',     (0.20, 0.20, 0.22), rough=0.7, metal=0.5)
    m.lamp_glow    = mk('LampGlow',     (1,0.95,0.7), rough=0.2, emit=(1,0.95,0.7), es=8.0)
    m.boat_hull    = mk('BoatHull',     (0.15, 0.18, 0.22), rough=0.75, metal=0.3)
    m.boat_white   = mk('BoatWhite',    (0.92, 0.90, 0.87), rough=0.80)
    m.torch_flame  = mk('TorchFlame',   (1,0.88,0.22), rough=0.15, metal=0.9,
                         emit=(1,0.72,0.1), es=10.0)
    m.gold         = mk('Gold',         (0.85,0.70,0.18), rough=0.12, metal=0.95)
    m.steel        = mk('Steel',        (0.55, 0.58, 0.60), rough=0.45, metal=0.7)
    m.antenna      = mk('Antenna',      (0.60, 0.62, 0.65), rough=0.40, metal=0.8)
    m.hydrant      = mk('Hydrant',      (0.85, 0.12, 0.08), rough=0.75)
    return m

# ─── Detailed Building Generator ──────────────────────────────────────────────

def add_building(col, x, y, w, d, h, mat, rng, m, style='modern'):
    """Detailed building with window grids, setbacks, and rooftop features."""
    name = f'Bld_{x:.0f}_{y:.0f}'

    # ── Main body ──────────────────────────────────────────────────────────
    # For taller buildings, add Art Deco setbacks
    setback_floors = []
    if style == 'art_deco' and h > 16:
        # 2-3 setback tiers
        tier1_h = h * 0.55
        tier2_h = h * 0.25
        tier3_h = h * 0.20
        # Base (widest)
        B(col, f'{name}_T0', (x, y, tier1_h/2), (w, d, tier1_h), mat)
        # Mid setback
        sw1 = w * 0.72; sd1 = d * 0.72
        B(col, f'{name}_T1', (x, y, tier1_h + tier2_h/2), (sw1, sd1, tier2_h), mat)
        # Top setback
        sw2 = w * 0.45; sd2 = d * 0.45
        B(col, f'{name}_T2', (x, y, tier1_h + tier2_h + tier3_h/2), (sw2, sd2, tier3_h), mat)
        # Spire on top
        if rng() > 0.3:
            spire_h = h * 0.15 + rng() * h * 0.1
            C(col, f'{name}_Spire', (x, y, h + spire_h/2), 0.12, spire_h, m.antenna, seg=6)
    elif style == 'setback' and h > 12:
        # Simple setback at 70%
        base_h = h * 0.7
        top_h = h * 0.3
        B(col, f'{name}_Base', (x, y, base_h/2), (w, d, base_h), mat)
        sw = w * 0.65; sd = d * 0.65
        B(col, f'{name}_Top', (x, y, base_h + top_h/2), (sw, sd, top_h), mat)
    else:
        # Simple box
        B(col, f'{name}_Body', (x, y, h/2), (w, d, h), mat)

    # ── Window grid (horizontal floor bands + vertical mullions) ───────────
    floor_h = 3.2
    num_floors = max(1, int(h / floor_h))

    # Front and back face window grids
    for face_y, face_name in [(y - d/2, 'F'), (y + d/2, 'B')]:
        # Horizontal floor bands
        for fi in range(1, num_floors):
            fz = fi * floor_h
            if fz < h - 0.5:
                B(col, f'{name}_HBand_{face_name}_{fi}',
                  (x, face_y, fz), (w + 0.06, 0.06, 0.12), m.win_frame)
        # Vertical mullions (every ~2 units)
        num_mullions = max(2, int(w / 2.0))
        for mi in range(num_mullions + 1):
            mx = x - w/2 + mi * w / num_mullions
            B(col, f'{name}_VMul_{face_name}_{mi}',
              (mx, face_y, min(h, h)/2), (0.08, 0.06, min(h, h) - 0.5), m.win_frame)

    # Left and right face window grids
    for face_x, face_name in [(x - w/2, 'L'), (x + w/2, 'R')]:
        for fi in range(1, num_floors):
            fz = fi * floor_h
            if fz < h - 0.5:
                B(col, f'{name}_HBand_{face_name}_{fi}',
                  (face_x, y, fz), (0.06, d + 0.06, 0.12), m.win_frame)
        num_mullions_s = max(2, int(d / 2.0))
        for mi in range(num_mullions_s + 1):
            my = y - d/2 + mi * d / num_mullions_s
            B(col, f'{name}_VMul_{face_name}_{mi}',
              (face_x, my, min(h, h)/2), (0.06, 0.08, min(h, h) - 0.5), m.win_frame)

    # ── Ground floor awning / entrance ─────────────────────────────────────
    if rng() > 0.3:
        B(col, f'{name}_Awning', (x, y - d/2 - 0.3, 1.5), (w * 0.6, 0.6, 0.08),
          mk(f'{name}_AwCol', (rng()*0.3+0.1, rng()*0.15+0.05, rng()*0.1), rough=0.85))

    # ── Rooftop features ──────────────────────────────────────────────────
    # Water tower
    if rng() > 0.4 and h > 6 and style != 'art_deco':
        wtx = x + (rng() - 0.5) * w * 0.4
        wty = y + (rng() - 0.5) * d * 0.4
        # Legs
        for li in range(4):
            lx = wtx + (0.2 if li < 2 else -0.2)
            ly = wty + (0.2 if li % 2 == 0 else -0.2)
            C(col, f'{name}_WTLeg_{li}', (lx, ly, h + 0.3), 0.04, 0.6, m.tree_trunk, seg=4)
        C(col, f'{name}_WT', (wtx, wty, h + 0.8), 0.28, 0.55, m.brick_brown, seg=10)
        K(col, f'{name}_WTCap', (wtx, wty, h + 1.15), 0.3, 0.02, 0.25,
          mk(f'WTCap', (0.05,0.05,0.05), rough=0.9), seg=10)

    # Mechanical penthouse
    if rng() > 0.5 and h > 10:
        pw = w * 0.3; pd = d * 0.3
        B(col, f'{name}_Mech', (x + (rng()-0.5)*w*0.2, y + (rng()-0.5)*d*0.2, h + 0.6),
          (pw, pd, 1.0), m.concrete)

    # Antenna
    if rng() > 0.7 and h > 18:
        C(col, f'{name}_Ant', (x, y, h + 1.5), 0.05, 2.5, m.antenna, seg=4)


# ─── Geographic Layout ────────────────────────────────────────────────────────
# Real NYC, 1 unit ≈ 30m
# Battery Park = origin (0, 0)
# Y+ = uptown (north), X+ = east (toward Brooklyn)
# Hudson River = west (x < -5), East River = east (x > 12 at tip, widens north)

# ── Statue of Liberty ────────────────────────────────────────────────────────

def build_statue_of_liberty(col, m, ox=-45, oy=-65):
    """SoL on Liberty Island, ~2.6km SW of Battery Park."""
    MV = m.verdigris; MG = m.granite; MT = m.torch_flame; MGL = m.gold

    # Liberty Island
    bpy.ops.mesh.primitive_cylinder_add(radius=6, depth=0.6, vertices=10, location=(ox, oy, 0.3))
    isle = bpy.context.active_object; isle.name = 'SOL_Island'
    isle.data.materials.append(m.park_grass); L(col, isle)

    # Star fort (octagonal)
    bpy.ops.mesh.primitive_cylinder_add(radius=4.5, depth=3.0, vertices=8, location=(ox, oy, 2.0))
    fort = bpy.context.active_object; fort.name = 'SOL_Fort'; fort.data.materials.append(MG); L(col, fort)

    # Pedestal tiers
    B(col, 'SOL_Ped0', (ox, oy, 4.5), (6.0, 6.0, 0.6), MG)
    B(col, 'SOL_Ped1', (ox, oy, 5.8), (5.0, 5.0, 2.0), MG)
    B(col, 'SOL_Ped2', (ox, oy, 8.0), (3.8, 3.8, 2.0), MG)
    B(col, 'SOL_Ped3', (ox, oy, 9.5), (3.0, 3.0, 0.6), MG)

    # Statue body
    z0 = 10.0
    K(col, 'SOL_Hem',   (ox, oy, z0+0.8),  1.8, 1.3, 1.6, MV, seg=16)
    C(col, 'SOL_Skirt',  (ox, oy, z0+2.8), 1.3, 3.5, MV, seg=14)
    K(col, 'SOL_Torso',  (ox, oy, z0+5.2), 1.1, 1.0, 2.5, MV, seg=14)
    C(col, 'SOL_Chest',  (ox, oy, z0+7.0), 1.0, 2.0, MV, seg=12)
    C(col, 'SOL_Neck',   (ox, oy, z0+8.4), 0.35, 0.6, MV, seg=10)
    S(col, 'SOL_Head',   (ox, oy, z0+9.3), 0.65, MV, seg=14)

    # Crown spikes
    for i in range(7):
        a = i / 7 * math.pi * 2
        sx = ox + math.cos(a) * 0.55
        sy = oy + math.sin(a) * 0.55
        K(col, f'SOL_Spike_{i}', (sx, sy, z0+10.0),
          0.08, 0.01, 0.9, MV, rot=(math.radians(20)*math.cos(a), math.radians(20)*math.sin(a), 0), seg=6)

    # Right arm + torch
    C(col, 'SOL_RArm', (ox+1.0, oy, z0+7.5), 0.22, 2.5, MV,
      rot=(0, math.radians(-50), 0), seg=8)
    C(col, 'SOL_RFore', (ox+1.8, oy, z0+9.8), 0.18, 2.5, MV,
      rot=(math.radians(5), math.radians(-10), 0), seg=8)
    S(col, 'SOL_Fist', (ox+2.1, oy, z0+11.2), 0.22, MV, seg=8)
    C(col, 'SOL_TorchH', (ox+2.1, oy, z0+12.2), 0.10, 1.5, MGL, seg=8)
    K(col, 'SOL_TorchB', (ox+2.1, oy, z0+13.2), 0.28, 0.12, 0.5, MGL, seg=10)
    K(col, 'SOL_Flame',  (ox+2.1, oy, z0+13.8), 0.20, 0.02, 0.8, MT, seg=8)
    S(col, 'SOL_Glow',   (ox+2.1, oy, z0+13.6), 0.18,
      mk('SOL_FGlow', (1,0.65,0.05), rough=0.3, emit=(1,0.6,0.05), es=15.0), seg=8)

    # Left arm + tablet
    C(col, 'SOL_LArm', (ox-0.9, oy+0.2, z0+7.0), 0.20, 2.2, MV,
      rot=(math.radians(25), math.radians(18), 0), seg=8)
    B(col, 'SOL_Tablet', (ox-1.8, oy+0.5, z0+6.5), (0.7, 0.12, 1.0), MG,
      rot=(0.2, 0, -0.35))

    # Torch point light
    bpy.ops.object.light_add(type='POINT', location=(ox+2.1, oy, z0+14.0))
    tl = bpy.context.active_object; tl.name = 'SOL_TorchLight'
    tl.data.energy = 500; tl.data.color = (1.0, 0.65, 0.1)
    tl.data.shadow_soft_size = 0.5; L(col, tl)

    print(f"  ✓ Statue of Liberty at ({ox:.0f}, {oy:.0f})")

# ── Brooklyn Bridge ──────────────────────────────────────────────────────────

def build_brooklyn_bridge(col, m, start_x=12, start_y=4, end_x=42, end_y=2):
    """Bridge from Lower Manhattan east to Brooklyn Heights."""
    MS = m.bridge_stone; MC = m.bridge_cable; MR = m.asphalt

    dx = end_x - start_x; dy = end_y - start_y
    bridge_len = math.sqrt(dx*dx + dy*dy)
    angle = math.atan2(dy, dx)
    mid_x = (start_x + end_x) / 2; mid_y = (start_y + end_y) / 2

    DECK_Z = 4.5
    TOWER_H = 10.0

    # Tower positions (1/3 and 2/3 of span)
    towers = []
    for t in [0.33, 0.67]:
        tx = start_x + dx * t; ty = start_y + dy * t
        towers.append((tx, ty))

        # Two Gothic pylons per tower
        for off in [-1.2, 1.2]:
            # Offset perpendicular to bridge direction
            px = tx + math.sin(angle) * off
            py = ty - math.cos(angle) * off
            B(col, f'BB_Pylon_{t:.0f}_{off}', (px, py, TOWER_H/2), (1.0, 1.2, TOWER_H), MS)
            # Pointed cap
            K(col, f'BB_Cap_{t:.0f}_{off}', (px, py, TOWER_H + 0.8), 0.9, 0.06, 1.6, MS, seg=4)

        # Cross beam
        cx = tx; cy = ty
        B(col, f'BB_Cross_{t:.0f}', (cx, cy, TOWER_H - 0.5), (3.2, 1.2, 0.4), MS, rot=(0, 0, angle))
        # Gothic arch detail
        B(col, f'BB_ArchLow_{t:.0f}', (cx, cy, 3.5), (3.0, 1.2, 0.35), MS, rot=(0, 0, angle))
        B(col, f'BB_ArchMid_{t:.0f}', (cx, cy, 6.5), (2.5, 1.2, 0.35), MS, rot=(0, 0, angle))

    # Deck
    B(col, f'BB_Deck', (mid_x, mid_y, DECK_Z), (bridge_len + 5, 3.5, 0.35), MR, rot=(0, 0, angle))

    # Approach ramps
    ramp_len = 6
    for which, sign in [('Man', -1), ('Bkn', 1)]:
        rx = start_x + dx * (0.5 + sign * 0.55)
        ry = start_y + dy * (0.5 + sign * 0.55)
        B(col, f'BB_Ramp_{which}', (rx, ry, DECK_Z * 0.6), (ramp_len, 3.5, 0.35), MR, rot=(0, 0, angle))

    # Main cables (parabolic segments)
    for cable_off in [-1.5, 1.5]:
        STEPS = 30
        pts = []
        for si in range(STEPS + 1):
            t = si / STEPS
            px = start_x + dx * t; py = start_y + dy * t
            # Perpendicular offset
            px += math.sin(angle) * cable_off
            py -= math.cos(angle) * cable_off
            # Parabolic sag between towers
            # Sag at midpoint, rise to tower tops
            nearest_tower_t = min([0.33, 0.67], key=lambda tt: abs(t - tt))
            dist_to_tower = abs(t - nearest_tower_t) / 0.33  # 0 at tower, 1 at mid/end
            sag = DECK_Z + 1.0 + dist_to_tower * dist_to_tower * (TOWER_H - DECK_Z - 1.0)
            # Near ends, drop down
            if t < 0.15 or t > 0.85:
                edge_t = min(t, 1.0 - t) / 0.15
                sag = DECK_Z + 0.5 + edge_t * (sag - DECK_Z - 0.5)
            pz = sag if t > 0.1 and t < 0.9 else DECK_Z + 0.5
            # Blend more carefully
            pz = sag
            pts.append(Vector((px, py, pz)))

        for si in range(len(pts) - 1):
            p1, p2 = pts[si], pts[si+1]
            mid_pt = (p1 + p2) / 2; seg_v = p2 - p1; length = seg_v.length
            if length < 0.01: continue
            bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=length, vertices=5, location=mid_pt)
            cs = bpy.context.active_object; cs.name = f'BB_Cable_{cable_off}_{si}'
            rot_q = seg_v.normalized().to_track_quat('Z', 'Y')
            cs.rotation_euler = rot_q.to_euler()
            bpy.ops.object.transform_apply(rotation=True)
            cs.data.materials.append(MC); L(col, cs)

    # Vertical hanger cables
    for si in range(STEPS + 1):
        t = si / STEPS
        if t < 0.12 or t > 0.88: continue
        px = start_x + dx * t; py = start_y + dy * t
        nearest_tower_t = min([0.33, 0.67], key=lambda tt: abs(t - tt))
        dist_to_tower = abs(t - nearest_tower_t) / 0.33
        cable_z = DECK_Z + 1.0 + dist_to_tower * dist_to_tower * (TOWER_H - DECK_Z - 1.0)
        hanger_h = cable_z - DECK_Z - 0.2
        if hanger_h > 0.3:
            for cable_off in [-1.5, 1.5]:
                hx = px + math.sin(angle) * cable_off
                hy = py - math.cos(angle) * cable_off
                C(col, f'BB_Hang_{cable_off}_{si}', (hx, hy, (cable_z + DECK_Z)/2),
                  0.02, hanger_h, MC, seg=4)

    print(f"  ✓ Brooklyn Bridge from ({start_x},{start_y}) to ({end_x},{end_y})")

# ── Financial District ────────────────────────────────────────────────────────

def build_financial_district(col, m):
    """Lower Manhattan / Financial District — tall glass + art deco buildings."""
    random.seed(42)
    # FiDi: x=0..12, y=2..18
    buildings = [
        # (x, y, w, d, h, mat, style) — key real buildings approximated
        # One World Trade Center (Freedom Tower)
        (2, 10, 3.2, 3.2, 55, m.glass_blue, 'setback'),
        # 4 WTC
        (5, 8, 2.5, 2.5, 30, m.glass_dark, 'modern'),
        # 3 WTC
        (3, 7, 2.2, 2.2, 32, m.glass_teal, 'modern'),
        # Woolworth Building area
        (4, 15, 1.8, 1.8, 28, m.art_deco, 'art_deco'),
        # 70 Pine
        (8, 5, 1.5, 1.5, 25, m.art_deco, 'art_deco'),
        # Chase Manhattan Plaza
        (6, 12, 2.8, 2.8, 24, m.glass_dark, 'modern'),
        # 40 Wall Street
        (7, 8, 2.0, 2.0, 27, m.limestone, 'art_deco'),
        # NY Stock Exchange area
        (5, 6, 2.5, 2.5, 8, m.limestone, 'modern'),
    ]
    for bx_, by_, bw, bd, bh, bmat, bstyle in buildings:
        add_building(col, bx_, by_, bw, bd, bh, bmat, random.random, m, bstyle)

    # Infill buildings (varied)
    styles = ['modern', 'art_deco', 'setback']
    fidi_mats = [m.glass_blue, m.glass_dark, m.limestone, m.art_deco, m.brick_brown, m.concrete]
    for i in range(45):
        bx_ = random.uniform(-2, 13)
        by_ = random.uniform(1, 20)
        # Avoid overlap with key buildings (rough check)
        w = random.uniform(1.2, 3.0)
        d = random.uniform(1.2, 3.0)
        h = random.uniform(5, 22)
        mat = random.choice(fidi_mats)
        style = random.choice(styles) if h > 12 else 'modern'
        add_building(col, bx_, by_, w, d, h, mat, random.random, m, style)

    print("  ✓ Financial District built")

# ── Midtown Background ───────────────────────────────────────────────────────

def build_midtown(col, m):
    """Background midtown skyline (far north)."""
    random.seed(77)
    mid_mats = [m.glass_blue, m.glass_dark, m.glass_teal, m.limestone, m.concrete]
    for i in range(40):
        bx_ = random.uniform(-8, 12)
        by_ = random.uniform(40, 80)
        w = random.uniform(2.0, 5.0)
        d = random.uniform(2.0, 5.0)
        h = random.uniform(10, 45)
        mat = random.choice(mid_mats)
        style = 'art_deco' if random.random() > 0.6 else 'setback'
        add_building(col, bx_, by_, w, d, h, mat, random.random, m, style)
    # Empire State Building (approx location)
    B(col, 'ESB_Base', (2, 60, 15), (4, 4, 30), m.limestone)
    B(col, 'ESB_Mid',  (2, 60, 35), (2.8, 2.8, 12), m.limestone)
    B(col, 'ESB_Top',  (2, 60, 43), (1.5, 1.5, 6), m.limestone)
    C(col, 'ESB_Ant',  (2, 60, 48), 0.12, 5, m.antenna, seg=6)
    print("  ✓ Midtown background built")

# ── Brooklyn Heights ──────────────────────────────────────────────────────────

def build_brooklyn(col, m):
    """Brooklyn residential area east of the bridge."""
    random.seed(55)
    bk_mats = [m.brick_red, m.brick_brown, m.concrete, m.limestone]
    for i in range(35):
        bx_ = random.uniform(38, 70)
        by_ = random.uniform(-10, 20)
        w = random.uniform(1.2, 3.5)
        d = random.uniform(1.2, 3.5)
        h = random.uniform(3, 14)
        mat = random.choice(bk_mats)
        add_building(col, bx_, by_, w, d, h, mat, random.random, m, 'modern')
    print("  ✓ Brooklyn Heights built")

# ── Water Bodies ──────────────────────────────────────────────────────────────

def build_water(col, m):
    """Harbor, East River, Hudson River."""
    # Main harbor water — large plane
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, -40, -0.5))
    harbor = bpy.context.active_object; harbor.name = 'Harbor'
    harbor.data.materials.append(m.water)
    mod = harbor.modifiers.new('Wave', 'WAVE')
    mod.height = 0.3; mod.width = 4; mod.speed = 0.3
    L(col, harbor)

    # East River (east side)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(25, 20, -0.5))
    east_r = bpy.context.active_object; east_r.name = 'EastRiver'
    east_r.data.materials.append(m.water)
    mod2 = east_r.modifiers.new('Wave', 'WAVE')
    mod2.height = 0.2; mod2.width = 3; mod2.speed = 0.4
    L(col, east_r)

    # Hudson River (west side)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(-20, 20, -0.5))
    hudson = bpy.context.active_object; hudson.name = 'HudsonRiver'
    hudson.data.materials.append(m.water)
    L(col, hudson)

    # Governors Island
    bpy.ops.mesh.primitive_cylinder_add(radius=5, depth=0.5, vertices=10, location=(10, -22, 0.25))
    gov = bpy.context.active_object; gov.name = 'GovernorsIsland'
    gov.data.materials.append(m.park_grass); L(col, gov)

    print("  ✓ Water bodies built")

# ── Battery Park + Streets ────────────────────────────────────────────────────

def build_ground(col, m):
    """Ground plane, Battery Park, street grid."""
    # Manhattan ground plane
    B(col, 'Manhattan_Ground', (5, 20, -0.1), (25, 80, 0.2), m.asphalt)

    # Battery Park (green space at southern tip)
    B(col, 'BatteryPark', (-2, -1, 0.05), (10, 6, 0.15), m.park_grass)
    # Park paths
    B(col, 'ParkPath1', (-2, -1, 0.08), (1.0, 5.5, 0.06), m.sidewalk)
    B(col, 'ParkPath2', (-2, -1, 0.08), (8.0, 0.8, 0.06), m.sidewalk)

    # Trees in Battery Park
    random.seed(33)
    for i in range(20):
        tx = -6 + random.uniform(0, 8)
        ty = -3 + random.uniform(0, 5)
        th = random.uniform(2.0, 4.0)
        C(col, f'Tree_Trunk_{i}', (tx, ty, th/2), 0.12, th, m.tree_trunk, seg=5)
        S(col, f'Tree_Crown_{i}', (tx, ty, th + 0.8), 0.8 + random.uniform(0, 0.5), m.tree_leaf, seg=6)

    # Brooklyn ground
    B(col, 'Brooklyn_Ground', (54, 5, -0.1), (30, 35, 0.2), m.asphalt)

    # Street grid — major avenues (running N-S)
    for ax in [-4, 0, 5, 10]:
        B(col, f'Avenue_{ax}', (ax, 20, 0.0), (2.5, 60, 0.12), m.asphalt)
        # Yellow center line
        for di in range(20):
            B(col, f'YLine_{ax}_{di}', (ax, -8 + di*3, 0.04), (0.12, 1.5, 0.04), m.road_line)
        # Sidewalks
        B(col, f'Sidew_{ax}_E', (ax + 1.6, 20, 0.02), (1.0, 60, 0.10), m.sidewalk)
        B(col, f'Sidew_{ax}_W', (ax - 1.6, 20, 0.02), (1.0, 60, 0.10), m.sidewalk)

    # Cross streets (running E-W)
    for sy in range(2, 45, 4):
        B(col, f'Street_{sy}', (5, sy, 0.0), (18, 1.8, 0.12), m.asphalt)

    # Street lamps along avenues
    for ax in [0, 5, 10]:
        for li in range(12):
            lx = ax + 1.8
            ly = -4 + li * 4
            C(col, f'Lamp_{ax}_{li}', (lx, ly, 1.8), 0.06, 3.6, m.lamp_pole, seg=5)
            S(col, f'LampG_{ax}_{li}', (lx, ly, 3.8), 0.15, m.lamp_glow, seg=5)

    # Fire hydrants
    for hi in range(8):
        hx = 1.5 + (hi % 3) * 5
        hy = hi * 5
        C(col, f'Hydrant_{hi}', (hx, hy, 0.18), 0.10, 0.35, m.hydrant, seg=6)

    print("  ✓ Ground, parks, streets built")

# ── Harbor Boats ──────────────────────────────────────────────────────────────

def build_boats(col, m):
    """Ferries and boats in harbor."""
    boats = [(-20, -40), (-10, -50), (5, -35), (15, -55), (-30, -30), (20, -65)]
    for bi, (bx_, by_) in enumerate(boats):
        # Hull
        B(col, f'Boat_Hull_{bi}', (bx_, by_, 0.2), (1.5, 3.5, 0.6), m.boat_hull)
        # Cabin
        B(col, f'Boat_Cabin_{bi}', (bx_, by_+0.5, 0.8), (1.0, 1.5, 0.6), m.boat_white)
        # Wake (small white plane behind)
        B(col, f'Boat_Wake_{bi}', (bx_, by_-2.0, 0.05), (0.8, 1.5, 0.04),
          mk(f'Wake_{bi}', (0.85, 0.88, 0.90), rough=0.3, emit=(0.8,0.85,0.9), es=0.3))

    # Staten Island Ferry (larger, orange)
    fx, fy = -25, -55
    B(col, 'SIFerry_Hull', (fx, fy, 0.3), (3.0, 8.0, 1.2), mk('FerryOrange', (0.9,0.45,0.05), rough=0.75))
    B(col, 'SIFerry_Cabin', (fx, fy+1, 1.5), (2.5, 5.0, 1.5), m.boat_white)
    B(col, 'SIFerry_Bridge', (fx, fy+3, 2.8), (1.5, 1.5, 0.8), m.boat_white)

    print("  ✓ Harbor boats built")

# ── World + Lighting ──────────────────────────────────────────────────────────

def setup_world():
    world = bpy.data.worlds.new('NYCWorld')
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree; nt.nodes.clear()
    bg  = nt.nodes.new('ShaderNodeBackground')
    sky = nt.nodes.new('ShaderNodeTexSky')
    sky.sky_type = 'HOSEK_WILKIE'
    sky.sun_elevation = math.radians(14)
    sky.sun_rotation  = math.radians(200)
    sky.air_density   = 1.0
    sky.aerosol_density = 1.5
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg.inputs['Strength'].default_value = 1.1
    nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

def setup_lighting():
    bpy.ops.object.light_add(type='SUN', location=(60, -60, 80))
    sun = bpy.context.active_object; sun.name = 'Sun'
    sun.data.energy = 5.5; sun.data.color = (1, 0.91, 0.74)
    sun.rotation_euler = (math.radians(40), 0, math.radians(38))

    bpy.ops.object.light_add(type='AREA', location=(0, 30, 2))
    fill = bpy.context.active_object; fill.name = 'WaterBounce'
    fill.data.energy = 180; fill.data.color = (0.3, 0.55, 1.0)
    fill.data.size = 100; fill.rotation_euler = (math.radians(85), 0, 0)

    for i, (lx, ly, c) in enumerate([(-15,-50,(1,0.45,0.12)),(15,-50,(1,0.50,0.15)),(0,-30,(1,0.48,0.10))]):
        bpy.ops.object.light_add(type='POINT', location=(lx, ly, 2))
        gl = bpy.context.active_object; gl.name = f'CityGlow_{i}'
        gl.data.energy = 500; gl.data.color = c; gl.data.shadow_soft_size = 8

def setup_camera():
    bpy.ops.object.camera_add(location=(-30, -80, 40))
    cam = bpy.context.active_object; cam.name = 'NYCCam'
    target = Vector((5, 5, 15))
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 26
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 90
    cam.data.dof.aperture_fstop = 5.6
    bpy.context.scene.camera = cam

def setup_render():
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 256; sc.cycles.use_denoising = True
    sc.render.resolution_x = 2560; sc.render.resolution_y = 1440

# ─── Run ──────────────────────────────────────────────────────────────────────

print("=" * 56)
print("  NYC Detailed Scene — Biometric City")
print("=" * 56)

print("\n[1/10] Clearing scene...")
clear_scene()

m = init_mats()
col = bpy.data.collections.new('NYC_Detailed')
bpy.context.scene.collection.children.link(col)

print("[2/10] Building Statue of Liberty (Liberty Island, SW)...")
build_statue_of_liberty(col, m, ox=-45, oy=-65)

print("[3/10] Building Brooklyn Bridge (Manhattan → Brooklyn)...")
build_brooklyn_bridge(col, m, start_x=12, start_y=4, end_x=42, end_y=2)

print("[4/10] Building Financial District (Lower Manhattan)...")
build_financial_district(col, m)

print("[5/10] Building Midtown background skyline...")
build_midtown(col, m)

print("[6/10] Building Brooklyn Heights...")
build_brooklyn(col, m)

print("[7/10] Building water (Harbor + Rivers)...")
build_water(col, m)

print("[8/10] Building ground, parks, streets...")
build_ground(col, m)

print("[9/10] Building harbor boats...")
build_boats(col, m)

print("[10/10] Setting up world, lights, camera...")
setup_world()
setup_lighting()
setup_camera()
setup_render()

bpy.ops.object.select_all(action='SELECT')

print(f"\nTotal objects: {len(bpy.context.scene.objects)}")
print("\n✅ NYC Detailed scene complete!")
print("   NUMPAD 0 → camera, Z → Rendered, F12 to render")
