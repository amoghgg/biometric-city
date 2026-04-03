import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { CITIES } from './cities.js'
import { District, setCurrentCity } from './District.js'

export class CityGrid {
  constructor(scene) {
    this.scene = scene
    this.districts = {}
    this.cityKey = null
    this.group = new THREE.Group()
    this.blenderModel = null
    this.hasBlenderScene = false
    scene.add(this.group)
  }

  async loadCity(cityKey) {
    this.cityKey = cityKey
    setCurrentCity(cityKey)
    const config = CITIES[cityKey]

    // Clear previous
    Object.values(this.districts).forEach(d => d.dispose())
    this.districts = {}
    this.hasBlenderScene = false
    if (this.blenderModel) {
      this.blenderModel.traverse(c => {
        if (c.isMesh) { c.geometry?.dispose(); if (c.material) { if (Array.isArray(c.material)) c.material.forEach(m => m.dispose()); else c.material.dispose() } }
      })
      this.group.remove(this.blenderModel)
      this.blenderModel = null
    }
    while (this.group.children.length) {
      const c = this.group.children[0]
      if (c.geometry) c.geometry.dispose()
      if (c.material) { if (Array.isArray(c.material)) c.material.forEach(m => m.dispose()); else c.material.dispose() }
      this.group.remove(c)
    }

    if (cityKey === 'nyc') {
      await this._loadBlenderScene()
      // Data-only districts for biometric data overlay (no geometry)
      for (const [key, districtConfig] of Object.entries(config.districts)) {
        this.districts[key] = new District(key, districtConfig, this.group, { noGeometry: true })
      }
    } else {
      this._buildGround(cityKey, config)
      this._buildRoads(cityKey, config)
      for (const [key, districtConfig] of Object.entries(config.districts)) {
        this.districts[key] = new District(key, districtConfig, this.group)
      }
    }
  }

  async _loadBlenderScene() {
    const loader = new GLTFLoader()
    const gltf = await loader.loadAsync('/nyc_v2.glb')
    this.blenderModel = gltf.scene

    // Blender Z-up → GLTF Y-up handled by exporter.
    // Blender +Y (uptown) → GLTF -Z. Frontend +Z = north → flip Z.
    // Scale to fit: Blender model spans ~400 units, frontend city spans ~140 units
    const S = 0.35
    this.blenderModel.scale.set(S, S, -S)
    // Center the model in the frontend coordinate space
    this.blenderModel.position.set(0, 0, 0)

    this.blenderModel.traverse(c => {
      if (c.isMesh) {
        c.castShadow = true
        c.receiveShadow = true
        const mats = Array.isArray(c.material) ? c.material : [c.material]
        mats.forEach(m => { m.side = THREE.DoubleSide })
      }
    })

    this.group.add(this.blenderModel)
    this.hasBlenderScene = true
  }

  _buildGround(cityKey, config) {
    const [[minX, minZ], [maxX, maxZ]] = config.groundExtent
    const w = maxX - minX
    const d = maxZ - minZ

    if (cityKey === 'nyc') {
      // Manhattan island — elongated, tapered north and south ends
      this._buildManhattanIsland()
      // Brooklyn/Queens — eastern landmass
      const eastGeo = new THREE.PlaneGeometry(60, 100)
      const eastMesh = new THREE.Mesh(eastGeo, this._groundMat(config.islandColor))
      eastMesh.rotation.x = -Math.PI / 2
      eastMesh.position.set(48, 0, -30)
      eastMesh.receiveShadow = true
      this.group.add(eastMesh)
      // Bronx — northern landmass
      const bronxGeo = new THREE.PlaneGeometry(50, 35)
      const bronx = new THREE.Mesh(bronxGeo, this._groundMat(config.islandColor))
      bronx.rotation.x = -Math.PI / 2
      bronx.position.set(18, 0, 66)
      bronx.receiveShadow = true
      this.group.add(bronx)
    } else {
      // Mumbai peninsula — elongated tear-drop pointing south
      this._buildMumbaiPeninsula()
      // Thane area — eastern landmass
      const thaneGeo = new THREE.PlaneGeometry(45, 80)
      const thane = new THREE.Mesh(thaneGeo, this._groundMat(config.islandColor))
      thane.rotation.x = -Math.PI / 2
      thane.position.set(52, 0, 20)
      thane.receiveShadow = true
      this.group.add(thane)
    }
  }

  _groundMat(color) {
    return new THREE.MeshStandardMaterial({ color: new THREE.Color(color), roughness: 0.95, metalness: 0 })
  }

  _buildManhattanIsland() {
    // Manhattan: roughly 4:13 aspect, narrower at tips
    // Use ShapeGeometry for tapered island shape
    const shape = new THREE.Shape()
    shape.moveTo(-10, -65)  // south tip
    shape.bezierCurveTo(-12, -55, -14, -20, -13, 0)   // west shore south
    shape.bezierCurveTo(-14, 20,  -12, 45, -8,  68)    // west shore north
    shape.lineTo(4, 68)                                  // north end
    shape.bezierCurveTo(8, 55, 10, 30, 10, 10)          // east shore north
    shape.bezierCurveTo(12, -10, 14, -40, 10, -62)      // east shore south
    shape.bezierCurveTo(6, -68, -6, -70, -10, -65)      // south tip
    shape.closePath()

    const geo = new THREE.ShapeGeometry(shape, 20)
    const mat = this._groundMat('#1a1a1c')
    const island = new THREE.Mesh(geo, mat)
    island.rotation.x = -Math.PI / 2
    island.position.y = 0
    island.receiveShadow = true
    this.group.add(island)
  }

  _buildMumbaiPeninsula() {
    // Mumbai: narrow south tip at Colaba, widens going north
    const shape = new THREE.Shape()
    shape.moveTo(-10, -62)  // south tip (Colaba)
    shape.bezierCurveTo(-14, -50, -22, -30, -30, -10)  // west (Arabian Sea) coast north
    shape.bezierCurveTo(-34, 5,   -28, 20, -20, 32)     // Bandra area
    shape.bezierCurveTo(-15, 45,  -5,  55,  10, 65)     // Andheri / Borivali
    shape.lineTo(28, 65)                                  // north end
    shape.bezierCurveTo(35, 50,  38, 30,  32, 10)       // eastern coast north
    shape.bezierCurveTo(28, -10, 22, -35, 14, -55)      // east coast (harbor) south
    shape.bezierCurveTo(8, -63, -4, -66, -10, -62)      // south tip
    shape.closePath()

    const geo = new THREE.ShapeGeometry(shape, 24)
    const mat = this._groundMat('#1a1810')
    const peninsula = new THREE.Mesh(geo, mat)
    peninsula.rotation.x = -Math.PI / 2
    peninsula.position.y = 0
    peninsula.receiveShadow = true
    this.group.add(peninsula)

    // Haji Ali islet — tiny island connected by causeway
    const isletGeo = new THREE.CylinderGeometry(2, 2.5, 0.3, 12)
    const islet = new THREE.Mesh(isletGeo, this._groundMat('#222018'))
    islet.position.set(-34, 0.15, -28)
    this.group.add(islet)
  }

  _buildRoads(cityKey, config) {
    const roadMat = new THREE.MeshStandardMaterial({ color: new THREE.Color(config.roadColor), roughness: 0.95 })

    if (cityKey === 'nyc') {
      // Manhattan grid: avenues run N-S, streets run E-W
      // Avenues (N-S), spaced ~2.5 units
      for (let x = -12; x <= 10; x += 2.5) {
        const geo = new THREE.PlaneGeometry(0.35, 135)
        const road = new THREE.Mesh(geo, roadMat)
        road.rotation.x = -Math.PI / 2
        road.position.set(x, 0.05, 0)
        this.group.add(road)
      }
      // Streets (E-W), spaced ~2.8 units
      for (let z = -65; z <= 65; z += 2.8) {
        const geo = new THREE.PlaneGeometry(25, 0.28)
        const road = new THREE.Mesh(geo, roadMat)
        road.rotation.x = -Math.PI / 2
        road.position.set(-1, 0.05, z)
        this.group.add(road)
      }
    } else {
      // Mumbai: more organic but main arteries
      // Western Express Highway (N-S on west)
      const weh = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 140), roadMat)
      weh.rotation.x = -Math.PI / 2; weh.position.set(-8, 0.05, 0); this.group.add(weh)
      // Central Railway line (N-S on east)
      const cr = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 140), roadMat)
      cr.rotation.x = -Math.PI / 2; cr.position.set(14, 0.05, 0); this.group.add(cr)
      // LBS Marg (N-S middle)
      const lbs = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 100), roadMat)
      lbs.rotation.x = -Math.PI / 2; lbs.position.set(4, 0.05, 10); this.group.add(lbs)
      // E-W connecting roads
      for (let z = -50; z <= 55; z += 12) {
        const geo = new THREE.PlaneGeometry(50, 0.4)
        const road = new THREE.Mesh(geo, roadMat)
        road.rotation.x = -Math.PI / 2
        road.position.set(0, 0.05, z)
        this.group.add(road)
      }
    }
  }

  applySnapshot(snapshot) {
    if (!snapshot?.districts) return
    for (const [key, data] of Object.entries(snapshot.districts)) {
      if (this.districts[key]) this.districts[key].updateData(data)
    }
  }

  tick(time) {
    Object.values(this.districts).forEach(d => d.tick(time))
  }

  getDistrictAtRay(raycaster) {
    const meshes = Object.values(this.districts).flatMap(d => d.getMeshes())
    const hits = raycaster.intersectObjects(meshes, false)
    if (!hits.length) return null
    const hit = hits[0]
    for (const [key, district] of Object.entries(this.districts)) {
      if (district.containsMesh(hit.object)) return { key, district, point: hit.point }
    }
    return null
  }

  dispose() {
    Object.values(this.districts).forEach(d => d.dispose())
    this.scene.remove(this.group)
  }
}
