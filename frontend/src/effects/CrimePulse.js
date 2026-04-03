import * as THREE from 'three'

// Ripple rings that expand from a point and fade — triggered on crime events
export class CrimePulse {
  constructor(scene) {
    this.scene = scene
    this.pulses = []
  }

  trigger(x, z, intensity = 0.5) {
    if (this.pulses.length > 12) return // cap simultaneous pulses

    const geo = new THREE.RingGeometry(0.1, 0.3, 32)
    const mat = new THREE.MeshBasicMaterial({
      color: 0xff2233,
      transparent: true,
      opacity: 0.8 * intensity,
      side: THREE.DoubleSide,
    })

    const mesh = new THREE.Mesh(geo, mat)
    mesh.rotation.x = -Math.PI / 2
    mesh.position.set(x, 0.3, z)

    this.scene.add(mesh)
    this.pulses.push({ mesh, mat, age: 0, intensity, x, z })
  }

  // Auto-trigger pulses based on city crime data
  autoTrigger(districts, cityConfig) {
    if (!cityConfig) return
    for (const [key, data] of Object.entries(districts)) {
      if (Math.random() < data.crime * 0.04) { // probability scales with crime
        const distConfig = cityConfig.districts[key]
        if (!distConfig) continue
        const [cx, cz] = distConfig.position
        const jx = cx + (Math.random() - 0.5) * distConfig.size[0]
        const jz = cz + (Math.random() - 0.5) * distConfig.size[1]
        this.trigger(jx, jz, data.crime)
      }
    }
  }

  tick(delta) {
    for (let i = this.pulses.length - 1; i >= 0; i--) {
      const p = this.pulses[i]
      p.age += delta

      const progress = p.age / 2.5 // 2.5 second lifetime
      const scale = 1 + progress * 18 * p.intensity
      p.mesh.scale.setScalar(scale)
      p.mat.opacity = (1 - progress) * 0.7 * p.intensity

      if (progress >= 1) {
        this.scene.remove(p.mesh)
        p.mesh.geometry.dispose()
        p.mat.dispose()
        this.pulses.splice(i, 1)
      }
    }
  }

  dispose() {
    this.pulses.forEach(p => {
      this.scene.remove(p.mesh)
      p.mesh.geometry.dispose()
      p.mat.dispose()
    })
    this.pulses = []
  }
}
