import * as THREE from 'three'

const STREET_COUNT = 800   // street-level: cars, people, bikes
const HIGH_COUNT   = 400   // elevated: helicopters, drones, high-floor windows

export class Particles {
  constructor(scene) {
    this.scene = scene
    this.crowd = 0.5

    this._buildStreetLayer()
    this._buildHighLayer()
  }

  _buildStreetLayer() {
    const count = STREET_COUNT
    const positions = new Float32Array(count * 3)
    const colors    = new Float32Array(count * 3)
    this.streetVel  = []

    for (let i = 0; i < count; i++) {
      positions[i * 3]     = (Math.random() - 0.5) * 180
      positions[i * 3 + 1] = 0.3 + Math.random() * 3.5  // street level
      positions[i * 3 + 2] = (Math.random() - 0.5) * 180

      // Car headlights: warm white with slight amber/cold variation
      const t = Math.random()
      if (t < 0.5) {
        // Warm headlight
        colors[i * 3] = 1.0; colors[i * 3 + 1] = 0.92; colors[i * 3 + 2] = 0.70
      } else if (t < 0.75) {
        // Cool LED headlight
        colors[i * 3] = 0.85; colors[i * 3 + 1] = 0.92; colors[i * 3 + 2] = 1.0
      } else {
        // Tail-light red
        colors[i * 3] = 1.0; colors[i * 3 + 1] = 0.15; colors[i * 3 + 2] = 0.05
      }

      this.streetVel.push({
        x: (Math.random() - 0.5) * 0.055,
        z: (Math.random() - 0.5) * 0.055,
        y: (Math.random() - 0.5) * 0.003,
      })
    }

    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geo.setAttribute('color',    new THREE.BufferAttribute(colors, 3))

    const mat = new THREE.PointsMaterial({
      vertexColors: true,
      size: 0.28,
      transparent: true,
      opacity: 0.72,
      sizeAttenuation: true,
      depthWrite: false,
    })

    this.streetPoints = new THREE.Points(geo, mat)
    this.streetGeo    = geo
    this.streetMat    = mat
    this.scene.add(this.streetPoints)
  }

  _buildHighLayer() {
    const count = HIGH_COUNT
    const positions = new Float32Array(count * 3)
    const colors    = new Float32Array(count * 3)
    this.highVel    = []

    for (let i = 0; i < count; i++) {
      positions[i * 3]     = (Math.random() - 0.5) * 220
      positions[i * 3 + 1] = 8 + Math.random() * 30  // elevated
      positions[i * 3 + 2] = (Math.random() - 0.5) * 220

      // High-altitude lights: navigation lights, chopper, lit windows at distance
      const t = Math.random()
      if (t < 0.4) {
        // Amber/orange window glow seen from distance
        colors[i * 3] = 1.0; colors[i * 3 + 1] = 0.78; colors[i * 3 + 2] = 0.30
      } else if (t < 0.65) {
        // White nav / strobe
        colors[i * 3] = 0.95; colors[i * 3 + 1] = 0.95; colors[i * 3 + 2] = 1.0
      } else {
        // Red blinker
        colors[i * 3] = 1.0; colors[i * 3 + 1] = 0.05; colors[i * 3 + 2] = 0.05
      }

      this.highVel.push({
        x: (Math.random() - 0.5) * 0.025,
        z: (Math.random() - 0.5) * 0.025,
        y: (Math.random() - 0.5) * 0.006,
      })
    }

    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geo.setAttribute('color',    new THREE.BufferAttribute(colors, 3))

    const mat = new THREE.PointsMaterial({
      vertexColors: true,
      size: 0.18,
      transparent: true,
      opacity: 0.55,
      sizeAttenuation: true,
      depthWrite: false,
    })

    this.highPoints = new THREE.Points(geo, mat)
    this.highGeo    = geo
    this.highMat    = mat
    this.scene.add(this.highPoints)
  }

  setCrowd(value) {
    this.crowd = value
    this.streetMat.opacity = 0.15 + value * 0.70
    this.highMat.opacity   = 0.10 + value * 0.50
  }

  tick() {
    const speedMult = 0.25 + this.crowd * 1.4

    // Street particles
    const sp = this.streetGeo.attributes.position.array
    for (let i = 0; i < STREET_COUNT; i++) {
      sp[i * 3]     += this.streetVel[i].x * speedMult
      sp[i * 3 + 1] += this.streetVel[i].y * speedMult
      sp[i * 3 + 2] += this.streetVel[i].z * speedMult
      if (sp[i * 3]     >  92) sp[i * 3]     = -92
      if (sp[i * 3]     < -92) sp[i * 3]     =  92
      if (sp[i * 3 + 2] >  92) sp[i * 3 + 2] = -92
      if (sp[i * 3 + 2] < -92) sp[i * 3 + 2] =  92
      if (sp[i * 3 + 1] >  4.5) sp[i * 3 + 1] = 0.3
      if (sp[i * 3 + 1] <  0.2) sp[i * 3 + 1] = 0.3
    }
    this.streetGeo.attributes.position.needsUpdate = true

    // High-altitude particles
    const hp = this.highGeo.attributes.position.array
    for (let i = 0; i < HIGH_COUNT; i++) {
      hp[i * 3]     += this.highVel[i].x
      hp[i * 3 + 1] += this.highVel[i].y
      hp[i * 3 + 2] += this.highVel[i].z
      if (hp[i * 3]     >  110) hp[i * 3]     = -110
      if (hp[i * 3]     < -110) hp[i * 3]     =  110
      if (hp[i * 3 + 2] >  110) hp[i * 3 + 2] = -110
      if (hp[i * 3 + 2] < -110) hp[i * 3 + 2] =  110
      if (hp[i * 3 + 1] >  40) hp[i * 3 + 1] = 8
      if (hp[i * 3 + 1] <   7) hp[i * 3 + 1] = 8
    }
    this.highGeo.attributes.position.needsUpdate = true
  }

  dispose() {
    this.streetGeo.dispose(); this.streetMat.dispose(); this.scene.remove(this.streetPoints)
    this.highGeo.dispose();   this.highMat.dispose();   this.scene.remove(this.highPoints)
  }
}
