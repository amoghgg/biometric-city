import * as THREE from 'three'

function seededRng(seed) {
  let s = seed
  return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646 }
}

export class Clouds {
  constructor(scene) {
    this.scene = scene
    this.formations = []
    this.group = new THREE.Group()
    scene.add(this.group)
    this._generate()
  }

  _generate() {
    const rng = seededRng(42)
    const count = 32

    for (let i = 0; i < count; i++) {
      const formation = new THREE.Group()
      const cloudRng = seededRng(i * 13 + 7)

      // Each cloud = 8-14 overlapping small spheres
      const blobs = 8 + Math.floor(cloudRng() * 7)
      for (let b = 0; b < blobs; b++) {
        // Smaller spheres so they merge into fluffy mass, not individual boulders
        const r = 0.8 + cloudRng() * 1.4
        const geo = new THREE.SphereGeometry(r, 7, 5)

        const brightness = 0.92 + cloudRng() * 0.08  // very white
        const mat = new THREE.MeshStandardMaterial({
          color: new THREE.Color(brightness, brightness, brightness * 1.02),
          // Self-illuminate so they glow regardless of scene darkness
          emissive: new THREE.Color(0.9, 0.92, 1.0),
          emissiveIntensity: 0.35,
          transparent: true,
          opacity: 0.88 + cloudRng() * 0.1,
          roughness: 1.0,
          metalness: 0,
        })
        const blob = new THREE.Mesh(geo, mat)
        blob.position.set(
          (cloudRng() - 0.5) * 7,   // wider spread
          (cloudRng() - 0.4) * 1.8, // mostly flat (cloud shape)
          (cloudRng() - 0.5) * 5
        )
        formation.add(blob)
      }

      // Position high in sky — never overlapping the city
      formation.position.set(
        (rng() - 0.5) * 380,
        115 + rng() * 55,           // y=115–170, far above city
        (rng() - 0.5) * 320
      )
      formation.userData.speed = 0.6 + rng() * 1.2
      formation.userData.direction = rng() * Math.PI * 2

      this.group.add(formation)
      this.formations.push(formation)
    }
  }

  setCity(cityConfig) {
    const isMumbai = cityConfig.name === 'MUMBAI'
    const rng = seededRng(99)
    this.formations.forEach((f) => {
      if (isMumbai) {
        // Mumbai monsoon: lower ceiling, slightly grey-tinged, but NOT dark
        f.position.y = 80 + rng() * 35
        f.children.forEach(blob => {
          const c = 0.78 + rng() * 0.12   // 0.78–0.90 (light grey, not dark)
          blob.material.color.setRGB(c, c * 0.97, c * 0.93)
          blob.material.emissive.setRGB(0.7, 0.65, 0.6)
          blob.material.emissiveIntensity = 0.25
          blob.material.opacity = 0.82 + rng() * 0.14
        })
      } else {
        f.position.y = 115 + rng() * 55
        f.children.forEach(blob => {
          const c = 0.92 + rng() * 0.08
          blob.material.color.setRGB(c, c, c * 1.02)
          blob.material.emissive.setRGB(0.9, 0.92, 1.0)
          blob.material.emissiveIntensity = 0.35
          blob.material.opacity = 0.88 + rng() * 0.1
        })
      }
    })
  }

  tick(time) {
    for (const f of this.formations) {
      const s = f.userData.speed
      const dir = f.userData.direction
      f.position.x += Math.cos(dir) * s * 0.008
      f.position.z += Math.sin(dir) * s * 0.008

      // Wrap clouds at scene boundary
      if (f.position.x > 210)  f.position.x = -210
      if (f.position.x < -210) f.position.x =  210
      if (f.position.z > 180)  f.position.z = -180
      if (f.position.z < -180) f.position.z =  180

      // Gentle bobbing
      f.position.y += Math.sin(time * 0.12 + f.userData.direction) * 0.004
    }
  }

  dispose() {
    this.formations.forEach(f => {
      f.children.forEach(b => { b.geometry.dispose(); b.material.dispose() })
    })
    this.scene.remove(this.group)
  }
}
