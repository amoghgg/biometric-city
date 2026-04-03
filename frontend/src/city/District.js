import * as THREE from 'three'
import { CITY_PALETTES } from './cities.js'
import { getModelLibrary, PALETTE_MODEL_TYPE } from './ModelLibrary.js'
import { FLOOR_H } from './BuildingAssembler.js'

function seededRng(seed) {
  let s = seed
  return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646 }
}

function hexToColor(hex) { return new THREE.Color(hex) }

function pickColor(palette, rng) {
  return hexToColor(palette[Math.floor(rng() * palette.length)])
}

function varyColor(color, rng, amount = 0.12) {
  const c = color.clone()
  const delta = (rng() - 0.5) * amount
  c.r = Math.max(0, Math.min(1, c.r + delta))
  c.g = Math.max(0, Math.min(1, c.g + delta))
  c.b = Math.max(0, Math.min(1, c.b + delta))
  return c
}

let _currentCity = 'nyc'
export function setCurrentCity(city) { _currentCity = city }

export class District {
  constructor(key, config, parentGroup, options = {}) {
    this.key    = key
    this.config = config
    this.group  = new THREE.Group()
    this.buildings   = []
    this.decorations = []

    this.current = { height_multiplier: 0.5, lean: 0.2, aqi_normalized: 0.2, crime: 0.3, crowd: 0.5, noise: 0.4, sentiment: 0.6 }
    this.target  = { ...this.current }

    parentGroup.add(this.group)
    if (!options.noGeometry) this._build()
  }

  _build() {
    const seed = this.key.split('').reduce((a, c) => a + c.charCodeAt(0), 0) * 7
    const rng  = seededRng(seed)
    const [cx, cz] = this.config.position
    const [sw, sd] = this.config.size
    const { heightRange, widthRange, buildingCount, palette, windowTint,
            hasWaterTowers, hasChhajjas, roofStyle } = this.config

    const cityPalettes = CITY_PALETTES[_currentCity]
    const colors       = cityPalettes[palette] || cityPalettes[Object.keys(cityPalettes)[0]]

    // GLTF assembled buildings disabled — too many draw calls (30k+/frame)
    // BoxGeometry: 1 draw call per building → stays fast
    const useGLTF = false

    for (let i = 0; i < buildingCount; i++) {
      const w  = widthRange[0] + rng() * (widthRange[1] - widthRange[0])
      const d  = widthRange[0] + rng() * (widthRange[1] - widthRange[0])
      const h  = heightRange[0] + rng() * (heightRange[1] - heightRange[0])
      const px = cx + (rng() - 0.5) * sw
      const pz = cz + (rng() - 0.5) * sd

      const baseColor = varyColor(pickColor(colors, rng), rng, 0.08)

      // ── Assembled GLTF building path ───────────────────────────────────────
      if (useGLTF) {
        const style = PALETTE_MODEL_TYPE[palette] || 'concrete'
        const wTiles = Math.max(2, Math.round(w))
        const dTiles = Math.max(2, Math.round(d))
        const roofColor = baseColor.clone().multiplyScalar(0.55)
        const model = lib.buildBuilding({
          targetHeight: h,
          widthTiles: wTiles,
          depthTiles: dTiles,
          seed: seed + i * 37,
          wallColor: baseColor,
          roofColor,
          style,
          windowTint,
        })
        if (model) {
          model.position.set(px - wTiles / 2, 0, pz - dTiles / 2)
          model.rotation.y = Math.floor(rng() * 4) * (Math.PI / 2)
          model.userData.districtKey = this.key
          model.userData.baseH       = h
          this.group.add(model)
          this.buildings.push(model)
          continue
        }
      }

      // ── BoxGeometry fallback (or when no models downloaded yet) ────────────
      const isGlass  = palette.includes('glass') || palette.includes('corporate') || palette.includes('modern')
      const isBrick  = palette.includes('brick') || palette.includes('brownstone') || palette.includes('terracotta') || palette.includes('colonial') || palette.includes('bandra')
      const isConcrete = palette.includes('warehouse') || palette.includes('limestone') || palette.includes('art_deco')

      // PBR values tuned for nighttime city aesthetic
      const roughness = isGlass    ? 0.18 + rng() * 0.15   // tinted glass, not mirror
        : isBrick    ? 0.82 + rng() * 0.12   // rough fired brick/stone
        : isConcrete ? 0.70 + rng() * 0.18   // polished to rough concrete
        :              0.65 + rng() * 0.20   // generic

      const metalness = isGlass    ? 0.30 + rng() * 0.20   // reflective but not chrome
        : isBrick    ? 0.00 + rng() * 0.03   // non-metallic masonry
        : isConcrete ? 0.02 + rng() * 0.06   // almost none
        :              0.00 + rng() * 0.04

      // Window emissive
      const warmWindowColor = new THREE.Color(1.0, 0.82, 0.42)   // incandescent warm
      const coolWindowColor = new THREE.Color(0.40, 0.60, 0.90)   // LED cool blue-white
      const emissiveColor   = windowTint === 'warm' ? warmWindowColor : coolWindowColor

      // Subtle window glow
      const baseEmissive = isGlass ? 0.15 + rng() * 0.20   // 0.15–0.35
        : isBrick        ? 0.05 + rng() * 0.08             // 0.05–0.13
        : isConcrete     ? 0.06 + rng() * 0.10             // 0.06–0.16
        :                  0.06 + rng() * 0.10             // 0.06–0.16

      const mat = new THREE.MeshStandardMaterial({
        color: baseColor,
        roughness,
        metalness,
        emissive: emissiveColor,
        emissiveIntensity: baseEmissive,
        envMapIntensity: isGlass ? 0.6 : 0.3,
      })

      const geo  = new THREE.BoxGeometry(w, h, d)
      const mesh = new THREE.Mesh(geo, mat)
      mesh.position.set(px, h / 2, pz)
      mesh.castShadow    = true
      mesh.receiveShadow = true
      mesh.userData = { districtKey: this.key, baseH: h, baseY: h / 2, px, pz }
      this.group.add(mesh)
      this.buildings.push(mesh)

      // Rooftop details
      if (roofStyle === 'stepped' && h > 12 && rng() > 0.5) this._addSteppedRoof(px, h, pz, w, d, baseColor, rng)
      if (hasWaterTowers  && h > 4  && rng() > 0.55) this._addWaterTower(px, h, pz, w, d, rng)
      if (hasChhajjas     && h > 2)                   this._addChhajjas(px, h, pz, w, d, baseColor, rng)
      if (roofStyle === 'mixed' && h < 4 && rng() > 0.5) this._addSlopedRoof(px, h, pz, w, d, rng)
    }

    // Ground patch — wet asphalt (low roughness + slight emissive for puddle reflections)
    const groundMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(0x080810),
      roughness: 0.35,
      metalness: 0.12,
      emissive: new THREE.Color(0x0d0d18),
      emissiveIntensity: 0.45,
    })
    const groundGeo = new THREE.PlaneGeometry(sw + 4, sd + 4)
    const ground    = new THREE.Mesh(groundGeo, groundMat)
    ground.rotation.x = -Math.PI / 2
    ground.position.set(cx, 0.01, cz)
    ground.receiveShadow = true
    this.group.add(ground)
  }

  // ── Rooftop details (BoxGeometry path only) ─────────────────────────────────

  _addSteppedRoof(px, h, pz, w, d, baseColor, rng) {
    const steps = 2 + Math.floor(rng() * 2)
    let stepH = h, stepW = w, stepD = d
    for (let s = 0; s < steps; s++) {
      const sH = 1.5 + rng() * 3
      stepW *= 0.65; stepD *= 0.65; stepH += sH
      const stepMat = new THREE.MeshStandardMaterial({ color: varyColor(baseColor, rng, 0.05), roughness: 0.6, metalness: 0.05 })
      const step    = new THREE.Mesh(new THREE.BoxGeometry(stepW, sH, stepD), stepMat)
      step.position.set(px, stepH - sH / 2, pz)
      step.castShadow = true
      this.group.add(step); this.decorations.push(step)
    }
    const spire = new THREE.Mesh(
      new THREE.CylinderGeometry(0.04, 0.12, 3 + rng() * 4, 8),
      new THREE.MeshStandardMaterial({ color: 0xb8a080, metalness: 0.5, roughness: 0.3 })
    )
    spire.position.set(px, stepH + 1.5, pz)
    this.group.add(spire); this.decorations.push(spire)
  }

  _addWaterTower(px, h, pz, w, d, rng) {
    const ox = (rng() - 0.5) * w * 0.5
    const oz = (rng() - 0.5) * d * 0.5
    for (let i = 0; i < 4; i++) {
      const lx = ox + (i < 2 ? -0.15 : 0.15)
      const lz = oz + (i % 2 === 0 ? -0.15 : 0.15)
      const leg = new THREE.Mesh(
        new THREE.CylinderGeometry(0.03, 0.03, 0.5, 4),
        new THREE.MeshStandardMaterial({ color: 0x3a2010, roughness: 0.9 })
      )
      leg.position.set(px + lx, h + 0.25, pz + lz)
      this.group.add(leg); this.decorations.push(leg)
    }
    const tank = new THREE.Mesh(
      new THREE.CylinderGeometry(0.22, 0.22, 0.4, 10),
      new THREE.MeshStandardMaterial({ color: 0x5a3520, roughness: 0.9 })
    )
    tank.position.set(px + ox, h + 0.7, pz + oz)
    this.group.add(tank); this.decorations.push(tank)

    const cap = new THREE.Mesh(
      new THREE.ConeGeometry(0.24, 0.2, 10),
      new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.8 })
    )
    cap.position.set(px + ox, h + 1.0, pz + oz)
    this.group.add(cap); this.decorations.push(cap)
  }

  _addChhajjas(px, h, pz, w, d, baseColor, rng) {
    const floors   = Math.floor(h / 1.8)
    const slabColor = varyColor(baseColor, rng, 0.05)
    slabColor.multiplyScalar(0.75)
    const slabMat = new THREE.MeshStandardMaterial({ color: slabColor, roughness: 0.9 })
    for (let f = 1; f <= floors; f++) {
      const slab = new THREE.Mesh(new THREE.BoxGeometry(w + 0.5, 0.08, 0.4), slabMat)
      slab.position.set(px, f * 1.8, pz + d / 2 + 0.2)
      this.group.add(slab); this.decorations.push(slab)
    }
  }

  _addSlopedRoof(px, h, pz, w, d, rng) {
    const roof = new THREE.Mesh(
      new THREE.ConeGeometry(Math.max(w, d) * 0.75, 0.8, 4),
      new THREE.MeshStandardMaterial({ color: 0x8a2a10, roughness: 0.85 })
    )
    roof.position.set(px, h + 0.4, pz)
    roof.rotation.y = Math.PI / 4
    this.group.add(roof); this.decorations.push(roof)
  }

  // ── Data + tick ─────────────────────────────────────────────────────────────

  updateData(data) { this.target = { ...this.target, ...data } }

  tick(time) {
    const speed = 0.012
    for (const k of Object.keys(this.current)) {
      if (this.target[k] !== undefined)
        this.current[k] += (this.target[k] - this.current[k]) * speed
    }

    const h         = this.current.height_multiplier
    const sentiment = this.current.sentiment
    const crime     = this.current.crime
    const flicker   = crime > 0.5
      ? (0.85 + 0.15 * Math.sin(time * (3 + crime * 12) + this.group.position.x * 17.3))
      : 1.0
    const intensity = (0.5 + sentiment * 0.9) * flicker

    for (const mesh of this.buildings) {
      const { baseH, isGLTF, baseScale } = mesh.userData
      const heightMult = 0.4 + h * 1.6

      if (mesh.userData.isAssembled || isGLTF) {
        // Assembled/GLTF building: animate scale.y for height data
        const bs = mesh.userData.baseScale ?? 1
        mesh.scale.set(bs, bs * heightMult, bs)
        for (const mat of (mesh.userData.emissiveMats ?? [])) {
          mat.emissiveIntensity = intensity
        }
      } else {
        // ── BoxGeometry building: y-scale animation + emissive update ─────────
        const targetY = (baseH * heightMult) / baseH
        mesh.scale.y  += (targetY - mesh.scale.y) * 0.025
        mesh.position.y = (mesh.scale.y * baseH) / 2

        const mat = mesh.material
        if (mat?.emissive) mat.emissiveIntensity = intensity
      }
    }
  }

  getMeshes()        { return this.buildings }
  containsMesh(m)    { return this.buildings.includes(m) }
  getData()          { return { ...this.current } }

  dispose() {
    ;[...this.buildings, ...this.decorations].forEach(m => {
      if (m.userData?.isAssembled || m.userData?.isGLTF) {
        m.traverse(child => {
          if (child.isMesh) { child.geometry?.dispose(); child.material?.dispose() }
        })
      } else {
        if (m.geometry) m.geometry.dispose()
        if (m.material) m.material.dispose()
      }
      this.group.remove(m)
    })
    this.buildings   = []
    this.decorations = []
  }
}
