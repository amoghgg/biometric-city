import * as THREE from 'three'

// Controls scene-level fog and ambient color based on AQI + sentiment
export class Atmosphere {
  constructor(scene) {
    this.scene = scene
    this.aqi = 0.2

    // Exponential fog: thicker at distance
    scene.fog = new THREE.FogExp2(0x030a12, 0.0038)

    // Ambient — base fill for scene
    this.ambientLight = new THREE.AmbientLight(0x223355, 0.8)
    scene.add(this.ambientLight)

    // Hemisphere — sky bounce vs ground bounce
    this.hemiLight = new THREE.HemisphereLight(0x3a5580, 0x1a1205, 0.7)
    scene.add(this.hemiLight)

    // Key directional from above
    this.dirLight = new THREE.DirectionalLight(0xffffff, 0.55)
    this.dirLight.position.set(50, 100, 50)
    this.dirLight.castShadow = true
    scene.add(this.dirLight)

    // ── City light pollution ─────────────────────────────────────────────────
    // Subtle warm upward glow from streets — just enough to tint building bases
    this.cityGlow = new THREE.PointLight(0xff7733, 3.0, 180, 1.8)
    this.cityGlow.position.set(0, 2, 0)
    scene.add(this.cityGlow)

    // Scattered secondary glow nodes
    this.glowNodes = []
    const glowPositions = [
      [30,  2,  30, 0xff8844],
      [-30, 2, -30, 0xff9955],
      [20,  2, -40, 0xffaa44],
      [-20, 2,  35, 0xff7722],
    ]
    for (const [x, y, z, color] of glowPositions) {
      const pl = new THREE.PointLight(color, 0.8, 90, 2.0)
      pl.position.set(x, y, z)
      scene.add(pl)
      this.glowNodes.push(pl)
    }
  }

  update(aqiNormalized, sentiment) {
    this.aqi = aqiNormalized

    // Fog density: clean = thin, polluted = thick smoggy
    this.scene.fog.density = 0.0028 + aqiNormalized * 0.010

    // Fog color: clear night blue → dirty brownish haze
    const fogClean    = new THREE.Color(0x030a12)
    const fogPolluted = new THREE.Color(0x18100a)
    this.scene.fog.color.lerpColors(fogClean, fogPolluted, aqiNormalized)

    // Ambient mood: despair (dark blue) → joy (warm blue-white)
    const moodDark  = new THREE.Color(0x080e1a)
    const moodLight = new THREE.Color(0x1a2a44)
    this.ambientLight.color.lerpColors(moodDark, moodLight, sentiment)
    this.ambientLight.intensity = 0.35 + sentiment * 0.65

    // Hemi sky tint: clear sky → brown smog
    const skyClean    = new THREE.Color(0x3a5580)
    const skyPolluted = new THREE.Color(0x3a2210)
    this.hemiLight.color.lerpColors(skyClean, skyPolluted, aqiNormalized)

    // City glow intensity: subtle variation with sentiment
    const glowIntensity = 2.0 + sentiment * 2.0
    this.cityGlow.intensity = glowIntensity

    // Under heavy pollution, glow turns more orange-red (sodium lamp tint)
    const glowClean    = new THREE.Color(0xff7733)
    const glowPolluted = new THREE.Color(0xff4400)
    this.cityGlow.color.lerpColors(glowClean, glowPolluted, aqiNormalized * 0.6)
  }

  dispose() {
    this.scene.remove(this.ambientLight)
    this.scene.remove(this.hemiLight)
    this.scene.remove(this.dirLight)
    this.scene.remove(this.cityGlow)
    for (const n of this.glowNodes) this.scene.remove(n)
    this.scene.fog = null
  }
}
