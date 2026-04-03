import { gsap } from 'gsap'
import { CITIES } from '../city/cities.js'

export class CitySwitch {
  constructor(camera, cityGrid, onSwitch) {
    this.camera = camera
    this.cityGrid = cityGrid
    this.onSwitch = onSwitch
    this.currentCity = 'nyc'
    this.animating = false

    document.querySelectorAll('.city-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const city = btn.dataset.city
        if (city !== this.currentCity && !this.animating) {
          this._switchTo(city)
        }
      })
    })
  }

  async _switchTo(cityKey) {
    this.animating = true

    // Update button states
    document.querySelectorAll('.city-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.city === cityKey)
    })

    const config = CITIES[cityKey]

    // 1. Camera pulls back
    await gsap.to(this.camera.position, {
      y: 200, duration: 1.2, ease: 'power2.inOut'
    })

    // 2. Scale buildings down
    const districts = Object.values(this.cityGrid.districts)
    await gsap.to(districts.map(d => d.group.scale), {
      x: 0, y: 0, z: 0, duration: 0.8, ease: 'power2.in', stagger: 0.02
    })

    // 3. Load new city
    await this.cityGrid.loadCity(cityKey)
    this.currentCity = cityKey

    // 4. Scale buildings up staggered
    const newDistricts = Object.values(this.cityGrid.districts)
    newDistricts.forEach(d => { d.group.scale.set(0, 0, 0) })
    await gsap.to(newDistricts.map(d => d.group.scale), {
      x: 1, y: 1, z: 1, duration: 1.0, ease: 'back.out(1.2)', stagger: 0.04
    })

    // 5. Camera swoops to new default
    const cam = config.cameraDefault
    await gsap.to(this.camera.position, {
      x: cam.x, y: cam.y, z: cam.z, duration: 1.5, ease: 'power2.inOut'
    })

    this.animating = false
    this.onSwitch(cityKey)
  }
}
