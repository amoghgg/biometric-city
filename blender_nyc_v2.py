"""
NYC Detailed Scene v2 — Biometric City
Uses procedural window-grid materials instead of per-window geometry.
Geographic placement: 1 unit ≈ 30m, Battery Park = origin, Y+ = uptown, X+ = east
"""
import bpy, math, random
from mathutils import Vector

# ─── Helpers ──────────────────────────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for d in [bpy.data.meshes, bpy.data.materials, bpy.data.lights,
              bpy.data.curves, bpy.data.cameras]:
        for b in list(d): d.remove(b)

def L(col, obj):
    for c in obj.users_collection: c.objects.unlink(obj)
    col.objects.link(obj); return obj

def B(col, n, loc, sc, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = n; o.scale = sc; o.rotation_euler = rot
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
    o = bpy.context.active_object; o.name = n; o.data.materials.append(mat); return L(col, o)

# ─── Procedural Window Grid Materials ─────────────────────────────────────────
# Uses Brick Texture to create realistic window patterns (no geometry needed!)

def make_window_facade(name, wall_color, win_emit_color, roughness=0.80,
                       metalness=0.0, brick_scale=5.0, mortar_size=0.08,
                       emit_strength=1.5):
    """PBR material with procedural window grid pattern using Brick Texture."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()

    # Nodes
    coord  = nt.nodes.new('ShaderNodeTexCoord')
    mapping = nt.nodes.new('ShaderNodeMapping')
    brick  = nt.nodes.new('ShaderNodeTexBrick')
    bump   = nt.nodes.new('ShaderNodeBump')
    bsdf   = nt.nodes.new('ShaderNodeBsdfPrincipled')
    out    = nt.nodes.new('ShaderNodeOutputMaterial')

    # Brick Texture → simulates window grid
    # Color1 = window glass (dark), Color2 = window variant, Mortar = wall
    mapping.inputs['Scale'].default_value = (brick_scale, brick_scale * 1.5, brick_scale)
    brick.inputs['Color1'].default_value = (0.06, 0.10, 0.18, 1)   # dark window glass
    brick.inputs['Color2'].default_value = (0.08, 0.14, 0.24, 1)   # slightly lighter pane
    brick.inputs['Mortar'].default_value = (*wall_color, 1)         # wall/spandrel
    brick.inputs['Scale'].default_value  = brick_scale
    brick.inputs['Mortar Size'].default_value = mortar_size         # thick wall = smaller windows
    brick.inputs['Row Height'].default_value = 0.35
    brick.offset = 0.0  # aligned grid, not brick-style offset

    bump.inputs['Strength'].default_value = 0.3
    bump.inputs['Distance'].default_value = 0.15

    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value  = metalness
    bsdf.inputs['Emission Color'].default_value = (*win_emit_color, 1)
    bsdf.inputs['Emission Strength'].default_value = emit_strength

    # Wiring
    nt.links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    nt.links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
    nt.links.new(brick.outputs['Color'],  bsdf.inputs['Base Color'])
    nt.links.new(brick.outputs['Fac'],    bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'],  bsdf.inputs['Normal'])
    # Use Fac to drive emission (windows glow, wall doesn't)
    nt.links.new(brick.outputs['Fac'],    bsdf.inputs['Emission Strength'])
    nt.links.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])

    # Layout
    coord.location  = (-800, 0); mapping.location = (-600, 0)
    brick.location  = (-350, 0); bump.location = (-100, -200)
    bsdf.location   = (100, 0);  out.location = (400, 0)
    return mat

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

# ─── Material Library ─────────────────────────────────────────────────────────

def init_mats():
    M = {}
    # Window-grid facade materials (procedural)
    M['glass_modern'] = make_window_facade('GlassModern', (0.12, 0.18, 0.28),
        (0.4, 0.7, 1.0), roughness=0.06, metalness=0.82, brick_scale=6.0, mortar_size=0.04, emit_strength=2.5)
    M['glass_dark']   = make_window_facade('GlassDark', (0.06, 0.08, 0.14),
        (0.3, 0.55, 0.9), roughness=0.04, metalness=0.88, brick_scale=7.0, mortar_size=0.03, emit_strength=3.0)
    M['glass_teal']   = make_window_facade('GlassTeal', (0.10, 0.22, 0.28),
        (0.35, 0.80, 0.90), roughness=0.06, metalness=0.78, brick_scale=5.5, mortar_size=0.05, emit_strength=2.0)
    M['brick_red']    = make_window_facade('BrickRed', (0.60, 0.30, 0.16),
        (1.0, 0.82, 0.45), roughness=0.90, metalness=0.0, brick_scale=4.0, mortar_size=0.12, emit_strength=1.0)
    M['brick_brown']  = make_window_facade('BrickBrown', (0.50, 0.35, 0.20),
        (1.0, 0.85, 0.50), roughness=0.88, metalness=0.0, brick_scale=4.5, mortar_size=0.10, emit_strength=0.8)
    M['limestone']    = make_window_facade('Limestone', (0.78, 0.74, 0.62),
        (1.0, 0.90, 0.60), roughness=0.84, metalness=0.0, brick_scale=5.0, mortar_size=0.08, emit_strength=1.2)
    M['art_deco']     = make_window_facade('ArtDeco', (0.68, 0.64, 0.52),
        (1.0, 0.92, 0.65), roughness=0.82, metalness=0.02, brick_scale=4.0, mortar_size=0.06, emit_strength=1.5)
    M['concrete']     = make_window_facade('Concrete', (0.50, 0.48, 0.44),
        (0.9, 0.80, 0.55), roughness=0.88, metalness=0.0, brick_scale=5.0, mortar_size=0.10, emit_strength=0.7)
    # Plain materials
    M['asphalt']     = mk('Asphalt',     (0.08, 0.08, 0.10), rough=0.88)
    M['sidewalk']    = mk('Sidewalk',    (0.42, 0.40, 0.37), rough=0.90)
    M['water']       = mk('Water',       (0.01, 0.04, 0.10), rough=0.03, emit=(0.02,0.05,0.12), es=0.4)
    M['grass']       = mk('Grass',       (0.10, 0.35, 0.08), rough=0.95)
    M['trunk']       = mk('Trunk',       (0.30, 0.22, 0.12), rough=0.92)
    M['leaf']        = mk('Leaf',        (0.12, 0.42, 0.10), rough=0.90)
    M['verdigris']   = mk('Verdigris',   (0.18, 0.47, 0.38), rough=0.62, metal=0.25)
    M['granite']     = mk('Granite',     (0.50, 0.47, 0.43), rough=0.88)
    M['bridge_st']   = mk('BridgeSt',    (0.70, 0.65, 0.56), rough=0.88)
    M['cable']       = mk('Cable',       (0.28, 0.30, 0.32), rough=0.60, metal=0.8)
    M['road_line']   = mk('YellowLine',  (0.9,0.85,0.1), rough=0.85, emit=(0.9,0.85,0.1), es=0.4)
    M['lamp']        = mk('LampPole',    (0.20, 0.20, 0.22), rough=0.7, metal=0.5)
    M['lamp_glow']   = mk('LampGlow',    (1,0.95,0.7), rough=0.2, emit=(1,0.95,0.7), es=8.0)
    M['boat_hull']   = mk('BoatHull',    (0.15, 0.18, 0.22), rough=0.75, metal=0.3)
    M['boat_white']  = mk('BoatWhite',   (0.92, 0.90, 0.87), rough=0.80)
    M['torch']       = mk('Torch',       (1,0.88,0.22), rough=0.15, metal=0.9, emit=(1,0.72,0.1), es=10.0)
    M['gold']        = mk('Gold',        (0.85,0.70,0.18), rough=0.12, metal=0.95)
    M['steel']       = mk('Steel',       (0.55,0.58,0.60), rough=0.45, metal=0.7)
    M['antenna']     = mk('Antenna',     (0.60,0.62,0.65), rough=0.40, metal=0.8)
    M['hydrant']     = mk('Hydrant',     (0.85,0.12,0.08), rough=0.75)
    M['ferry_org']   = mk('FerryOrange', (0.9,0.45,0.05), rough=0.75)
    M['flame_glow']  = mk('FlameGlow',   (1,0.65,0.05), rough=0.3, emit=(1,0.6,0.05), es=15.0)
    M['wt_cap']      = mk('WTCap',       (0.05,0.05,0.05), rough=0.9)
    return M

# ─── Building Generator (efficient) ──────────────────────────────────────────

def add_bldg(col, x, y, w, d, h, mat_key, M, rng, style='modern'):
    """Single building with setbacks + rooftop detail, using procedural window mat."""
    name = f'B_{x:.0f}_{y:.0f}'
    mat = M[mat_key]

    if style == 'art_deco' and h > 16:
        t1 = h * 0.55; t2 = h * 0.25; t3 = h * 0.20
        B(col, f'{name}_0', (x, y, t1/2), (w, d, t1), mat)
        B(col, f'{name}_1', (x, y, t1+t2/2), (w*0.70, d*0.70, t2), mat)
        B(col, f'{name}_2', (x, y, t1+t2+t3/2), (w*0.42, d*0.42, t3), mat)
        if rng() > 0.3:
            C(col, f'{name}_Sp', (x, y, h + h*0.08), 0.10, h*0.15, M['antenna'], seg=5)
    elif style == 'setback' and h > 12:
        bh = h * 0.7; th = h * 0.3
        B(col, f'{name}_0', (x, y, bh/2), (w, d, bh), mat)
        B(col, f'{name}_1', (x, y, bh+th/2), (w*0.62, d*0.62, th), mat)
    else:
        B(col, f'{name}', (x, y, h/2), (w, d, h), mat)

    # Water tower
    if rng() > 0.45 and h > 6 and style != 'art_deco':
        wtx = x + (rng()-0.5)*w*0.35; wty = y + (rng()-0.5)*d*0.35
        C(col, f'{name}_WT', (wtx, wty, h+0.7), 0.26, 0.5, M['brick_brown'], seg=10)
        K(col, f'{name}_WTC', (wtx, wty, h+1.05), 0.28, 0.02, 0.22, M['wt_cap'], seg=10)

    # Mechanical penthouse
    if rng() > 0.6 and h > 10:
        B(col, f'{name}_Mh', (x+(rng()-0.5)*w*0.2, y+(rng()-0.5)*d*0.2, h+0.5),
          (w*0.28, d*0.28, 0.9), M['concrete'])

# ─── Statue of Liberty ───────────────────────────────────────────────────────

def build_sol(col, M, ox=-45, oy=-65):
    MV=M['verdigris']; MG=M['granite']; MT=M['torch']; MGL=M['gold']

    # Island
    bpy.ops.mesh.primitive_cylinder_add(radius=6, depth=0.6, vertices=10, location=(ox,oy,0.3))
    o=bpy.context.active_object; o.name='SOL_Isle'; o.data.materials.append(M['grass']); L(col,o)
    # Fort
    bpy.ops.mesh.primitive_cylinder_add(radius=4.5, depth=3, vertices=8, location=(ox,oy,2))
    o=bpy.context.active_object; o.name='SOL_Fort'; o.data.materials.append(MG); L(col,o)
    # Pedestal
    B(col,'SOL_P0',(ox,oy,4.5),(6,6,0.6),MG)
    B(col,'SOL_P1',(ox,oy,5.8),(5,5,2),MG)
    B(col,'SOL_P2',(ox,oy,8.0),(3.8,3.8,2),MG)
    B(col,'SOL_P3',(ox,oy,9.5),(3,3,0.6),MG)
    # Body
    z0=10
    K(col,'SOL_Hem',(ox,oy,z0+0.8),1.8,1.3,1.6,MV,seg=16)
    C(col,'SOL_Skirt',(ox,oy,z0+2.8),1.3,3.5,MV,seg=14)
    K(col,'SOL_Torso',(ox,oy,z0+5.2),1.1,1.0,2.5,MV,seg=14)
    C(col,'SOL_Chest',(ox,oy,z0+7),1.0,2,MV,seg=12)
    C(col,'SOL_Neck',(ox,oy,z0+8.4),0.35,0.6,MV,seg=10)
    S(col,'SOL_Head',(ox,oy,z0+9.3),0.65,MV,seg=14)
    # Crown spikes
    for i in range(7):
        a=i/7*math.pi*2
        K(col,f'SOL_Sp{i}',(ox+math.cos(a)*0.55,oy+math.sin(a)*0.55,z0+10),
          0.08,0.01,0.9,MV,rot=(math.radians(20)*math.cos(a),math.radians(20)*math.sin(a),0),seg=6)
    # Right arm + torch
    C(col,'SOL_RA',(ox+1,oy,z0+7.5),0.22,2.5,MV,rot=(0,math.radians(-50),0),seg=8)
    C(col,'SOL_RF',(ox+1.8,oy,z0+9.8),0.18,2.5,MV,rot=(math.radians(5),math.radians(-10),0),seg=8)
    S(col,'SOL_Fist',(ox+2.1,oy,z0+11.2),0.22,MV,seg=8)
    C(col,'SOL_TH',(ox+2.1,oy,z0+12.2),0.10,1.5,MGL,seg=8)
    K(col,'SOL_TB',(ox+2.1,oy,z0+13.2),0.28,0.12,0.5,MGL,seg=10)
    K(col,'SOL_Fl',(ox+2.1,oy,z0+13.8),0.20,0.02,0.8,MT,seg=8)
    S(col,'SOL_FG',(ox+2.1,oy,z0+13.6),0.18,M['flame_glow'],seg=8)
    # Left arm + tablet
    C(col,'SOL_LA',(ox-0.9,oy+0.2,z0+7),0.20,2.2,MV,rot=(math.radians(25),math.radians(18),0),seg=8)
    B(col,'SOL_Tab',(ox-1.8,oy+0.5,z0+6.5),(0.7,0.12,1),MG,rot=(0.2,0,-0.35))
    # Torch light
    bpy.ops.object.light_add(type='POINT',location=(ox+2.1,oy,z0+14))
    tl=bpy.context.active_object; tl.name='SOL_Light'
    tl.data.energy=500; tl.data.color=(1,0.65,0.1); tl.data.shadow_soft_size=0.5; L(col,tl)
    print(f"  ✓ Statue of Liberty at ({ox},{oy})")

# ─── Brooklyn Bridge ─────────────────────────────────────────────────────────

def build_bridge(col, M, sx=12, sy=4, ex=42, ey=2):
    MS=M['bridge_st']; MC=M['cable']; MR=M['asphalt']
    dx=ex-sx; dy=ey-sy; blen=math.sqrt(dx*dx+dy*dy); ang=math.atan2(dy,dx)
    mx=(sx+ex)/2; my=(sy+ey)/2; DZ=4.5; TH=10

    # Towers at 1/3 and 2/3
    for t in [0.33,0.67]:
        tx=sx+dx*t; ty=sy+dy*t
        for off in [-1.2,1.2]:
            px=tx+math.sin(ang)*off; py=ty-math.cos(ang)*off
            B(col,f'BB_Pyl_{t:.0f}_{off}',(px,py,TH/2),(1,1.2,TH),MS)
            K(col,f'BB_Cap_{t:.0f}_{off}',(px,py,TH+0.8),0.9,0.06,1.6,MS,seg=4)
        B(col,f'BB_X_{t:.0f}',(tx,ty,TH-0.5),(3.2,1.2,0.4),MS,rot=(0,0,ang))
        B(col,f'BB_AL_{t:.0f}',(tx,ty,3.5),(3,1.2,0.35),MS,rot=(0,0,ang))
        B(col,f'BB_AM_{t:.0f}',(tx,ty,6.5),(2.5,1.2,0.35),MS,rot=(0,0,ang))
    # Deck
    B(col,'BB_Deck',(mx,my,DZ),(blen+5,3.5,0.35),MR,rot=(0,0,ang))
    # Ramps
    for w,s in [('M',-1),('B',1)]:
        rx=sx+dx*(0.5+s*0.55); ry=sy+dy*(0.5+s*0.55)
        B(col,f'BB_R{w}',(rx,ry,DZ*0.6),(6,3.5,0.35),MR,rot=(0,0,ang))
    # Main cables
    STEPS=25
    for co in [-1.5,1.5]:
        pts=[]
        for si in range(STEPS+1):
            t_=si/STEPS
            px=sx+dx*t_+math.sin(ang)*co; py=sy+dy*t_-math.cos(ang)*co
            nt_=min([0.33,0.67],key=lambda tt:abs(t_-tt))
            dt=abs(t_-nt_)/0.33
            sag=DZ+1+dt*dt*(TH-DZ-1)
            if t_<0.12 or t_>0.88:
                et=min(t_,1-t_)/0.12; sag=DZ+0.5+et*(sag-DZ-0.5)
            pts.append(Vector((px,py,sag)))
        for si in range(len(pts)-1):
            p1,p2=pts[si],pts[si+1]; mid=(p1+p2)/2; sv=p2-p1; ln=sv.length
            if ln<0.01: continue
            bpy.ops.mesh.primitive_cylinder_add(radius=0.06,depth=ln,vertices=5,location=mid)
            cs=bpy.context.active_object; cs.name=f'BB_C{co}_{si}'
            cs.rotation_euler=sv.normalized().to_track_quat('Z','Y').to_euler()
            bpy.ops.object.transform_apply(rotation=True)
            cs.data.materials.append(MC); L(col,cs)
    # Hangers
    for si in range(STEPS+1):
        t_=si/STEPS
        if t_<0.14 or t_>0.86: continue
        px=sx+dx*t_; py=sy+dy*t_
        nt_=min([0.33,0.67],key=lambda tt:abs(t_-tt))
        dt=abs(t_-nt_)/0.33; cz=DZ+1+dt*dt*(TH-DZ-1); hh=cz-DZ-0.2
        if hh>0.3:
            for co in [-1.5,1.5]:
                hx=px+math.sin(ang)*co; hy=py-math.cos(ang)*co
                C(col,f'BB_H{co}_{si}',(hx,hy,(cz+DZ)/2),0.02,hh,MC,seg=4)
    print(f"  ✓ Brooklyn Bridge")

# ─── District Builders ────────────────────────────────────────────────────────

def build_fidi(col, M):
    random.seed(42)
    # Key buildings (approximate real positions)
    keys = [
        (2,10,3.2,3.2,55,'glass_modern','setback'),  # One WTC
        (5,8,2.5,2.5,30,'glass_dark','modern'),       # 4 WTC
        (3,7,2.2,2.2,32,'glass_teal','modern'),       # 3 WTC
        (4,15,1.8,1.8,28,'art_deco','art_deco'),      # Woolworth
        (8,5,1.5,1.5,25,'art_deco','art_deco'),       # 70 Pine
        (6,12,2.8,2.8,24,'glass_dark','modern'),      # Chase Plaza
        (7,8,2,2,27,'limestone','art_deco'),           # 40 Wall St
        (5,6,2.5,2.5,8,'limestone','modern'),          # NYSE area
    ]
    for bx_,by_,w,d,h,mk_,st in keys:
        add_bldg(col,bx_,by_,w,d,h,mk_,M,random.random,st)
    # Infill
    fmats=['glass_modern','glass_dark','limestone','art_deco','brick_brown','concrete']
    for i in range(50):
        add_bldg(col, random.uniform(-2,13), random.uniform(1,20),
                 random.uniform(1.2,3), random.uniform(1.2,3), random.uniform(5,22),
                 random.choice(fmats), M, random.random,
                 random.choice(['modern','art_deco','setback']) if random.random()>0.4 else 'modern')
    print("  ✓ Financial District")

def build_midtown(col, M):
    random.seed(77)
    mm=['glass_modern','glass_dark','glass_teal','limestone','concrete']
    for i in range(45):
        add_bldg(col, random.uniform(-8,12), random.uniform(40,80),
                 random.uniform(2,5), random.uniform(2,5), random.uniform(10,45),
                 random.choice(mm), M, random.random,
                 'art_deco' if random.random()>0.6 else 'setback')
    # ESB
    B(col,'ESB_0',(2,60,15),(4,4,30),M['limestone'])
    B(col,'ESB_1',(2,60,35),(2.8,2.8,12),M['limestone'])
    B(col,'ESB_2',(2,60,43),(1.5,1.5,6),M['limestone'])
    C(col,'ESB_A',(2,60,48),0.12,5,M['antenna'],seg=6)
    print("  ✓ Midtown")

def build_brooklyn(col, M):
    random.seed(55)
    bm=['brick_red','brick_brown','concrete','limestone']
    for i in range(40):
        add_bldg(col, random.uniform(38,70), random.uniform(-10,20),
                 random.uniform(1.2,3.5), random.uniform(1.2,3.5), random.uniform(3,14),
                 random.choice(bm), M, random.random, 'modern')
    print("  ✓ Brooklyn")

# ─── Water ────────────────────────────────────────────────────────────────────

def build_water(col, M):
    for name, pos, sz in [('Harbor',(0,-40,-0.5),400), ('EastR',(25,20,-0.5),200), ('Hudson',(-20,20,-0.5),200)]:
        bpy.ops.mesh.primitive_plane_add(size=sz, location=pos)
        o=bpy.context.active_object; o.name=name; o.data.materials.append(M['water'])
        if name=='Harbor':
            mod=o.modifiers.new('W','WAVE'); mod.height=0.3; mod.width=4; mod.speed=0.3
        L(col,o)
    # Governors Island
    bpy.ops.mesh.primitive_cylinder_add(radius=5, depth=0.5, vertices=10, location=(10,-22,0.25))
    o=bpy.context.active_object; o.name='GovIsland'; o.data.materials.append(M['grass']); L(col,o)
    print("  ✓ Water")

# ─── Ground + Streets + Trees ─────────────────────────────────────────────────

def build_ground(col, M):
    B(col,'ManhGnd',(5,20,-0.1),(25,80,0.2),M['asphalt'])
    B(col,'BkGnd',(54,5,-0.1),(30,35,0.2),M['asphalt'])
    B(col,'BattPark',(-2,-1,0.05),(10,6,0.15),M['grass'])
    B(col,'PPath1',(-2,-1,0.08),(1,5.5,0.06),M['sidewalk'])
    B(col,'PPath2',(-2,-1,0.08),(8,0.8,0.06),M['sidewalk'])
    # Trees in park
    random.seed(33)
    for i in range(22):
        tx=-6+random.uniform(0,8); ty=-3+random.uniform(0,5); th=random.uniform(2,4)
        C(col,f'Tr{i}',(tx,ty,th/2),0.12,th,M['trunk'],seg=5)
        S(col,f'TrC{i}',(tx,ty,th+0.8),0.8+random.uniform(0,0.5),M['leaf'],seg=6)
    # Avenues
    for ax in [-4,0,5,10]:
        B(col,f'Ave{ax}',(ax,20,0),(2.5,60,0.12),M['asphalt'])
        B(col,f'SW{ax}E',(ax+1.6,20,0.02),(1,60,0.1),M['sidewalk'])
        B(col,f'SW{ax}W',(ax-1.6,20,0.02),(1,60,0.1),M['sidewalk'])
        for di in range(20):
            B(col,f'YL{ax}_{di}',(ax,-8+di*3,0.04),(0.12,1.5,0.04),M['road_line'])
    for sy in range(2,45,4):
        B(col,f'St{sy}',(5,sy,0),(18,1.8,0.12),M['asphalt'])
    # Street lamps
    for ax in [0,5,10]:
        for li in range(12):
            C(col,f'Lp{ax}_{li}',(ax+1.8,-4+li*4,1.8),0.06,3.6,M['lamp'],seg=5)
            S(col,f'LG{ax}_{li}',(ax+1.8,-4+li*4,3.8),0.15,M['lamp_glow'],seg=5)
    # Hydrants
    for hi in range(8):
        C(col,f'Hy{hi}',(1.5+(hi%3)*5,hi*5,0.18),0.10,0.35,M['hydrant'],seg=6)
    print("  ✓ Ground")

# ─── Boats ────────────────────────────────────────────────────────────────────

def build_boats(col, M):
    for bi,(bx_,by_) in enumerate([(-20,-40),(-10,-50),(5,-35),(15,-55),(-30,-30),(20,-65)]):
        B(col,f'Bt{bi}',(bx_,by_,0.2),(1.5,3.5,0.6),M['boat_hull'])
        B(col,f'BtC{bi}',(bx_,by_+0.5,0.8),(1,1.5,0.6),M['boat_white'])
    # SI Ferry
    B(col,'SIF_H',(-25,-55,0.3),(3,8,1.2),M['ferry_org'])
    B(col,'SIF_C',(-25,-54,1.5),(2.5,5,1.5),M['boat_white'])
    B(col,'SIF_B',(-25,-52,2.8),(1.5,1.5,0.8),M['boat_white'])
    print("  ✓ Boats")

# ─── World + Lighting + Camera ────────────────────────────────────────────────

def setup_all():
    world = bpy.data.worlds.new('NYCWorld')
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree; nt.nodes.clear()
    bg=nt.nodes.new('ShaderNodeBackground')
    sky=nt.nodes.new('ShaderNodeTexSky')
    sky.sky_type='HOSEK_WILKIE'; sky.sun_elevation=math.radians(14)
    sky.sun_rotation=math.radians(200); sky.air_density=1.0; sky.aerosol_density=1.5
    out=nt.nodes.new('ShaderNodeOutputWorld')
    bg.inputs['Strength'].default_value=1.1
    nt.links.new(sky.outputs['Color'],bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'],out.inputs['Surface'])

    bpy.ops.object.light_add(type='SUN',location=(60,-60,80))
    sun=bpy.context.active_object; sun.name='Sun'; sun.data.energy=5.5
    sun.data.color=(1,0.91,0.74); sun.rotation_euler=(math.radians(40),0,math.radians(38))

    bpy.ops.object.light_add(type='AREA',location=(0,30,2))
    f=bpy.context.active_object; f.name='Fill'; f.data.energy=180
    f.data.color=(0.3,0.55,1); f.data.size=100; f.rotation_euler=(math.radians(85),0,0)

    for i,(lx,ly,c) in enumerate([(-15,-50,(1,0.45,0.12)),(15,-50,(1,0.50,0.15)),(0,-30,(1,0.48,0.10))]):
        bpy.ops.object.light_add(type='POINT',location=(lx,ly,2))
        g=bpy.context.active_object; g.name=f'Glow{i}'; g.data.energy=500; g.data.color=c; g.data.shadow_soft_size=8

    bpy.ops.object.camera_add(location=(-30,-80,40))
    cam=bpy.context.active_object; cam.name='Cam'
    d=Vector((5,5,15))-cam.location
    cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    cam.data.lens=26; cam.data.dof.use_dof=True
    cam.data.dof.focus_distance=90; cam.data.dof.aperture_fstop=5.6
    bpy.context.scene.camera=cam

    sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=256; sc.cycles.use_denoising=True
    sc.render.resolution_x=2560; sc.render.resolution_y=1440

# ─── Run ──────────────────────────────────────────────────────────────────────

print("=" * 52)
print("  NYC v2 — Procedural Windows + Geographic Layout")
print("=" * 52)

print("\n[1] Clearing...")
clear_scene()
M = init_mats()
col = bpy.data.collections.new('NYC_v2')
bpy.context.scene.collection.children.link(col)

print("[2] Statue of Liberty (Liberty Island, SW of Manhattan)...")
build_sol(col, M, ox=-45, oy=-65)

print("[3] Brooklyn Bridge (Lower Manhattan → Brooklyn)...")
build_bridge(col, M, sx=12, sy=4, ex=42, ey=2)

print("[4] Financial District (southern Manhattan)...")
build_fidi(col, M)

print("[5] Midtown skyline (background)...")
build_midtown(col, M)

print("[6] Brooklyn Heights...")
build_brooklyn(col, M)

print("[7] Harbor + Rivers...")
build_water(col, M)

print("[8] Ground, parks, streets, trees...")
build_ground(col, M)

print("[9] Harbor boats + ferry...")
build_boats(col, M)

print("[10] World, lights, camera...")
setup_all()

print(f"\nTotal objects: {len(bpy.context.scene.objects)}")
print("\n✅ NYC v2 complete!")
