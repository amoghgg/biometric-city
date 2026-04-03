import * as THREE from 'three'

// Hand-crafted landmark buildings for NYC and Mumbai

export class Landmarks {
  constructor(scene) {
    this.scene = scene
    this.group = new THREE.Group()
    scene.add(this.group)
    this.city = null
  }

  loadCity(cityKey) {
    // Clear old landmarks
    while (this.group.children.length) {
      const c = this.group.children[0]
      if (c.geometry) c.geometry.dispose()
      if (c.material) c.material.dispose()
      this.group.remove(c)
    }
    this.city = cityKey
    if (cityKey === 'nyc') this._buildNYC()
    else this._buildMumbai()
  }

  _mat(color, rough = 0.5, metal = 0, emissive = 0x000000, emissInt = 0) {
    return new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: metal, emissive, emissiveIntensity: emissInt })
  }

  _box(w, h, d, color, rough, metal) {
    const g = new THREE.BoxGeometry(w, h, d)
    const m = this._mat(color, rough, metal)
    return new THREE.Mesh(g, m)
  }

  _cyl(rt, rb, h, segs, color, rough, metal) {
    const g = new THREE.CylinderGeometry(rt, rb, h, segs)
    return new THREE.Mesh(g, this._mat(color, rough, metal))
  }

  // ─── NYC Landmarks ────────────────────────────────────────────────────────

  _buildNYC() {
    this._empireState()
    this._oneWTC()
    this._chryslerBuilding()
    this._brooklynBridge()
    this._statuOfLiberty()
    this._hudsonRiverPiers()
  }

  _empireState() {
    const g = new THREE.Group()
    // Base tower
    const base = this._box(3.5, 32, 3.5, 0xc8b890, 0.55, 0.05); base.position.y = 16; g.add(base)
    // Steps
    const s1  = this._box(3.0, 6, 3.0, 0xd4c49a, 0.5, 0.05); s1.position.y = 35; g.add(s1)
    const s2  = this._box(2.4, 5, 2.4, 0xd8caa0, 0.5, 0.05); s2.position.y = 43; g.add(s2)
    const s3  = this._box(1.8, 4, 1.8, 0xddd0a8, 0.5, 0.05); s3.position.y = 50; g.add(s3)
    // Crown
    const crown = this._cyl(0.5, 0.8, 3, 8, 0xb8a060, 0.4, 0.2); crown.position.y = 55.5; g.add(crown)
    // Mooring mast / spire
    const mast = this._cyl(0.04, 0.1, 10, 6, 0xe8e0b0, 0.3, 0.5); mast.position.y = 62; g.add(mast)
    // Broadcast antenna
    const ant  = this._cyl(0.02, 0.02, 6, 4, 0xffffff, 0.5, 0.3);  ant.position.y = 69; g.add(ant)
    // Emissive crown lights
    const lightGeo = new THREE.SphereGeometry(0.3, 8, 8)
    const lightMat = new THREE.MeshStandardMaterial({ color: 0xffcc44, emissive: 0xffaa00, emissiveIntensity: 2.0 })
    for (let i = 0; i < 4; i++) {
      const l = new THREE.Mesh(lightGeo, lightMat)
      const a = (i / 4) * Math.PI * 2
      l.position.set(Math.cos(a) * 1.0, 56, Math.sin(a) * 1.0)
      g.add(l)
    }
    g.position.set(-2, 0, 12)
    this.group.add(g)
  }

  _oneWTC() {
    const g = new THREE.Group()
    // Tapered octagonal prism — One WTC
    const h = 48
    const points = []
    for (let i = 0; i <= h; i++) {
      const t = i / h
      // Square at base, 45° rotated square at top — creates twist
      const r = 2.2 * (1 - t * 0.35)
      points.push(new THREE.Vector2(r, i))
    }
    // Approximate with stacked boxes that taper
    const towerMat = new THREE.MeshStandardMaterial({ color: 0x4488cc, roughness: 0.1, metalness: 0.4, emissive: 0x112244, emissiveIntensity: 0.3 })
    for (let i = 0; i < 8; i++) {
      const t = i / 8
      const s = 4.2 * (1 - t * 0.3)
      const segH = h / 8
      const seg = new THREE.Mesh(new THREE.BoxGeometry(s, segH, s), towerMat)
      seg.position.y = i * segH + segH / 2
      seg.rotation.y = t * Math.PI / 4
      g.add(seg)
    }
    // Spire
    const spire = this._cyl(0.02, 0.08, 14, 6, 0xddeeff, 0.3, 0.6)
    spire.position.y = 50
    g.add(spire)
    g.position.set(-7, 0, -52)
    this.group.add(g)
  }

  _chryslerBuilding() {
    const g = new THREE.Group()
    // Base
    const base = this._box(2.8, 26, 2.8, 0xa89060, 0.5, 0.1); base.position.y = 13; g.add(base)
    // Steps
    const s1 = this._box(2.3, 5, 2.3, 0xb0986a, 0.45, 0.1); s1.position.y = 29; g.add(s1)
    const s2 = this._box(1.8, 4, 1.8, 0xb8a070, 0.45, 0.1); s2.position.y = 35; g.add(s2)
    const s3 = this._box(1.3, 3, 1.3, 0xc0a878, 0.4, 0.15); s3.position.y = 40; g.add(s3)
    // Stainless steel sunburst crown — multiple arcs
    const crownMat = new THREE.MeshStandardMaterial({ color: 0xd8d0b8, roughness: 0.15, metalness: 0.8, emissive: 0x888060, emissiveIntensity: 0.2 })
    for (let i = 0; i < 6; i++) {
      const arcGeo = new THREE.TorusGeometry(0.9, 0.08, 4, 12, Math.PI * 0.4)
      const arc = new THREE.Mesh(arcGeo, crownMat)
      arc.position.y = 42 + i * 0.4
      arc.rotation.y = (i / 6) * Math.PI * 2
      arc.rotation.x = -0.2
      g.add(arc)
    }
    // Needle
    const needle = this._cyl(0.02, 0.08, 8, 6, 0xe8e0c8, 0.2, 0.7)
    needle.position.y = 48; g.add(needle)
    g.position.set(6, 0, 11)
    this.group.add(g)
  }

  _brooklynBridge() {
    const g = new THREE.Group()
    const stoneMat = this._mat(0x8a7a68, 0.85, 0.0)
    const cableMat = this._mat(0x404040, 0.6, 0.2)
    const deckMat  = this._mat(0x3a3a3c, 0.9, 0.0)

    // Two Gothic towers
    for (let side = 0; side < 2; side++) {
      const x = side === 0 ? 2 : 24  // Manhattan side vs Brooklyn side
      const tower = new THREE.Group()
      // Main shaft
      const shaft = new THREE.Mesh(new THREE.BoxGeometry(1.2, 10, 0.8), stoneMat)
      shaft.position.y = 5; tower.add(shaft)
      // Gothic arch openings (approximated as darker boxes)
      const archMat = this._mat(0x2a2420, 0.95)
      const arch1 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 2.5, 0.85), archMat)
      arch1.position.set(0, 4, 0); tower.add(arch1)
      const arch2 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 2.5, 0.85), archMat)
      arch2.position.set(0, 7, 0); tower.add(arch2)
      // Turrets
      for (let t = 0; t < 2; t++) {
        const tur = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 1.5, 8), stoneMat)
        tur.position.set(t === 0 ? -0.5 : 0.5, 10.75, 0); tower.add(tur)
        const turCap = new THREE.Mesh(new THREE.ConeGeometry(0.27, 0.6, 8), stoneMat)
        turCap.position.set(t === 0 ? -0.5 : 0.5, 11.8, 0); tower.add(turCap)
      }
      tower.position.set(x, 0, -42)
      g.add(tower)
    }

    // Suspension cables — main catenary + hangers
    const cablePoints = []
    for (let i = 0; i <= 30; i++) {
      const t = i / 30
      const x = 2 + t * 22
      const y = 10 - 4 * Math.sin(Math.PI * t) // catenary shape
      cablePoints.push(new THREE.Vector3(x, y, -42))
    }
    const cableCurve = new THREE.CatmullRomCurve3(cablePoints)
    const cableGeo = new THREE.TubeGeometry(cableCurve, 30, 0.04, 4, false)
    g.add(new THREE.Mesh(cableGeo, cableMat))
    // Mirror cable
    const cablePoints2 = cablePoints.map(p => new THREE.Vector3(p.x, p.y, -42 + 0.6))
    const cableCurve2 = new THREE.CatmullRomCurve3(cablePoints2)
    const cableGeo2 = new THREE.TubeGeometry(cableCurve2, 30, 0.04, 4, false)
    g.add(new THREE.Mesh(cableGeo2, cableMat))

    // Road deck
    const deck = new THREE.Mesh(new THREE.BoxGeometry(24, 0.15, 0.7), deckMat)
    deck.position.set(13, 1.5, -42); g.add(deck)

    this.group.add(g)
  }

  _statuOfLiberty() {
    const g = new THREE.Group()
    // Pedestal island
    const island = new THREE.Mesh(new THREE.CylinderGeometry(1.8, 2, 0.4, 12), this._mat(0x3a5a2a, 0.9))
    island.position.y = 0.2; g.add(island)
    // Stone pedestal
    const ped = new THREE.Mesh(new THREE.BoxGeometry(1.2, 2, 1.2), this._mat(0x8a7a60, 0.85))
    ped.position.y = 1.4; g.add(ped)
    // Statue body (simplified)
    const body = this._cyl(0.3, 0.4, 2, 8, 0x7a9a70, 0.7, 0.05); body.position.y = 3.4; g.add(body)
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 8), this._mat(0x7a9a70, 0.7, 0.05))
    head.position.y = 4.7; g.add(head)
    // Crown spikes
    for (let i = 0; i < 7; i++) {
      const spike = this._cyl(0.02, 0.04, 0.35, 4, 0x8aaa80, 0.6)
      const a = (i / 7) * Math.PI * 2
      spike.position.set(Math.cos(a) * 0.22, 5.0, Math.sin(a) * 0.22)
      g.add(spike)
    }
    // Torch arm
    const arm = this._cyl(0.05, 0.05, 0.8, 4, 0x8aaa80, 0.7)
    arm.rotation.z = -Math.PI / 4; arm.position.set(-0.5, 4.0, 0); g.add(arm)
    const flame = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 6), this._mat(0xffcc00, 0.3, 0, 0xffaa00, 3.0))
    flame.position.set(-0.88, 4.55, 0); g.add(flame)
    g.position.set(-22, 0, -74)
    this.group.add(g)
  }

  _hudsonRiverPiers() {
    const pierMat = this._mat(0x3a3028, 0.9)
    for (let i = 0; i < 5; i++) {
      const pier = new THREE.Mesh(new THREE.BoxGeometry(3, 0.2, 0.5), pierMat)
      pier.position.set(-26, 0.1, -40 + i * 14)
      this.group.add(pier)
    }
  }

  // ─── Mumbai Landmarks ─────────────────────────────────────────────────────

  _buildMumbai() {
    this._gatewayOfIndia()
    this._bandraSealink()
    this._antilia()
    this._hajiAli()
    this._marineDrivePromenade()
  }

  _gatewayOfIndia() {
    const g = new THREE.Group()
    const stoneMat = this._mat(0xd4a840, 0.8, 0)
    const darkMat  = this._mat(0x2a1808, 0.9)

    // Main arch — two square towers connected by arch
    const towerL = new THREE.Mesh(new THREE.BoxGeometry(1.5, 8, 2), stoneMat)
    towerL.position.set(-2, 4, 0); g.add(towerL)
    const towerR = new THREE.Mesh(new THREE.BoxGeometry(1.5, 8, 2), stoneMat)
    towerR.position.set(2, 4, 0); g.add(towerR)
    // Arch lintel
    const lintel = new THREE.Mesh(new THREE.BoxGeometry(5, 1, 2), stoneMat)
    lintel.position.set(0, 8, 0); g.add(lintel)
    // Arch opening (dark)
    const arch = new THREE.Mesh(new THREE.BoxGeometry(2, 4, 2.1), darkMat)
    arch.position.set(0, 6, 0); g.add(arch)
    // Dome on top
    const dome = new THREE.Mesh(new THREE.SphereGeometry(1.0, 12, 8, 0, Math.PI * 2, 0, Math.PI * 0.5), stoneMat)
    dome.position.set(0, 9.5, 0); g.add(dome)
    // Small corner turrets
    for (let i = 0; i < 4; i++) {
      const tx = (i < 2 ? -2.5 : 2.5)
      const tz = (i % 2 === 0 ? -0.8 : 0.8)
      const tur = this._cyl(0.3, 0.3, 5, 8, 0xd4a840, 0.8)
      tur.position.set(tx, 4, tz); g.add(tur)
      const turCap = new THREE.Mesh(new THREE.ConeGeometry(0.32, 0.7, 8), stoneMat)
      turCap.position.set(tx, 6.85, tz); g.add(turCap)
    }
    g.position.set(-18, 0, -56)
    this.group.add(g)
  }

  _bandraSealink() {
    const g = new THREE.Group()
    const concreteMat = this._mat(0xc8c0b0, 0.85, 0)
    const cableMat    = this._mat(0xe0d8c8, 0.5, 0.3)
    const roadMat     = this._mat(0x2a2826, 0.9)

    // Two cable-stay pylons
    const pylonPositions = [
      { x: -26, z: -20 },
      { x: -34, z: -32 },
    ]

    for (const pos of pylonPositions) {
      // Main shaft
      const shaft = new THREE.Mesh(new THREE.BoxGeometry(0.6, 14, 0.6), concreteMat)
      shaft.position.set(pos.x, 7, pos.z); g.add(shaft)
      // Cross arm (A-frame)
      const armL = new THREE.Mesh(new THREE.BoxGeometry(0.2, 5, 0.2), concreteMat)
      armL.position.set(pos.x - 0.6, 12, pos.z); armL.rotation.z = 0.3; g.add(armL)
      const armR = new THREE.Mesh(new THREE.BoxGeometry(0.2, 5, 0.2), concreteMat)
      armR.position.set(pos.x + 0.6, 12, pos.z); armR.rotation.z = -0.3; g.add(armR)
    }

    // Cable stays — fan pattern from pylon tops
    const cableGeometry = new THREE.BufferGeometry()
    const cableVerts = []
    for (let i = 0; i < 2; i++) {
      const pylon = pylonPositions[i]
      for (let c = 0; c < 6; c++) {
        const t = c / 5
        const anchorX = pylon.x + (t - 0.5) * 8
        const anchorZ = pylon.z + (i === 0 ? t * 6 : -t * 6)
        cableVerts.push(pylon.x, 14, pylon.z)
        cableVerts.push(anchorX, 0.5, anchorZ)
      }
    }
    cableGeometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(cableVerts), 3))
    const cables = new THREE.LineSegments(cableGeometry, new THREE.LineBasicMaterial({ color: 0xe0d8c8 }))
    g.add(cables)

    // Road deck
    const road = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.15, 18), roadMat)
    road.position.set(-30, 0.5, -26); g.add(road)

    this.group.add(g)
  }

  _antilia() {
    const g = new THREE.Group()
    // Antilia: 27 floors, each floor slightly different / offset — stacked plates
    for (let i = 0; i < 12; i++) {
      const t = i / 12
      const w = 2.5 + Math.sin(t * Math.PI * 2) * 0.4
      const d = 1.8 + Math.cos(t * Math.PI * 3) * 0.3
      const offsetX = Math.sin(t * Math.PI * 1.5) * 0.3
      const h = 1.2
      const colors = [0x1a3050, 0x2a4060, 0x152840, 0x1e3548, 0x243f58]
      const col = colors[i % colors.length]
      const seg = this._box(w, h, d, col, 0.15, 0.35)
      seg.position.set(-20 + offsetX, i * h + h / 2, -30)
      seg.castShadow = true
      g.add(seg)
    }
    this.group.add(g)
  }

  _hajiAli() {
    const g = new THREE.Group()
    // Small tidal islet
    const islet = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.8, 0.3, 12), this._mat(0x9a9080, 0.9))
    islet.position.y = 0.15; g.add(islet)
    // White dargah walls
    const wallMat = this._mat(0xf0ece0, 0.85)
    const wall = new THREE.Mesh(new THREE.BoxGeometry(2.2, 1.5, 2.2), wallMat)
    wall.position.y = 1.0; g.add(wall)
    // Central dome
    const dome = new THREE.Mesh(new THREE.SphereGeometry(0.65, 12, 8, 0, Math.PI * 2, 0, Math.PI * 0.6), wallMat)
    dome.position.y = 2.2; g.add(dome)
    // Minaret
    const minaret = this._cyl(0.14, 0.18, 3.5, 8, 0xf0ece0, 0.85)
    minaret.position.set(0.9, 2.0, 0.9); g.add(minaret)
    const minaretCap = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.5, 8), wallMat)
    minaretCap.position.set(0.9, 3.95, 0.9); g.add(minaretCap)
    // Crescent
    const crescentMat = this._mat(0xffd700, 0.3, 0.7)
    const crescent = new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.025, 4, 12, Math.PI * 1.5), crescentMat)
    crescent.position.set(0.9, 4.55, 0.9); crescent.rotation.z = Math.PI / 4; g.add(crescent)
    // Narrow causeway from shore
    const causeway = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.08, 5), this._mat(0x8a8070, 0.9))
    causeway.position.set(0, 0.04, 3.5); g.add(causeway)

    g.position.set(-32, 0, -28)
    this.group.add(g)
  }

  _marineDrivePromenade() {
    // Art deco facade strip along Marine Drive
    const mat = this._mat(0xe8e4d0, 0.85)
    // Tetrapod wave-breakers along the waterfront
    const tetMat = this._mat(0x6a6060, 0.9)
    for (let i = 0; i < 12; i++) {
      const tet = this._cyl(0.2, 0.2, 0.3, 4, 0x6a6060, 0.9)
      tet.position.set(-38 + i * 0.6, 0.15, -36 + Math.sin(i * 0.8) * 0.5)
      this.group.add(tet)
    }
    // Street lamps along the curve
    for (let i = 0; i < 8; i++) {
      const t = i / 7
      const lx = -35 + t * 15
      const lz = -48 + t * 16
      const post = this._cyl(0.04, 0.04, 1.5, 4, 0x4a4848, 0.7)
      post.position.set(lx, 0.75, lz)
      const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 6), this._mat(0xffee88, 0.3, 0, 0xffcc44, 1.5))
      lamp.position.set(lx, 1.6, lz)
      this.group.add(post)
      this.group.add(lamp)
    }
  }

  tick(time) {
    // Animate lighthouse/statue torch
  }

  dispose() {
    this.scene.remove(this.group)
  }
}
