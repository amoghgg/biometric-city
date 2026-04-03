import { CITIES } from '../city/cities.js'

export class Tooltip {
  constructor() {
    this.el = document.getElementById('tooltip')
    this.nameEl = document.getElementById('tooltip-name')
    this.bodyEl = document.getElementById('tooltip-body')
    this.visible = false
  }

  show(districtKey, data, cityKey, screenX, screenY) {
    const cityConfig = CITIES[cityKey]
    const label = cityConfig?.districts[districtKey]?.label || districtKey

    this.nameEl.textContent = label.toUpperCase()
    this.bodyEl.innerHTML = this._buildRows(data, cityKey)

    // Position near cursor but keep in viewport
    const pad = 16
    const tw = 180, th = 140
    const x = Math.min(screenX + 16, window.innerWidth - tw - pad)
    const y = Math.min(screenY - 20, window.innerHeight - th - pad)
    this.el.style.left = `${x}px`
    this.el.style.top  = `${y}px`
    this.el.style.display = 'block'
  }

  hide() {
    this.el.style.display = 'none'
  }

  _buildRows(data, cityKey) {
    const rentLabel = cityKey === 'nyc' ? `$${data.rent}/mo` : `₹${data.rent}k/mo`
    const aqiClass  = data.aqi < 50 ? 'color:#00ffcc' : data.aqi < 100 ? 'color:#f39c12' : 'color:#ff3a3a'

    return `
      <div style="display:flex;justify-content:space-between;margin-bottom:3px">
        <span style="color:rgba(255,255,255,0.4)">RENT</span>
        <span>${rentLabel}</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:3px">
        <span style="color:rgba(255,255,255,0.4)">AQI</span>
        <span style="${aqiClass}">${Math.round(data.aqi)}</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:3px">
        <span style="color:rgba(255,255,255,0.4)">CRIME</span>
        <span>${data.crime_count_24h} / 24h</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:3px">
        <span style="color:rgba(255,255,255,0.4)">CROWD</span>
        <span>${Math.round(data.crowd * 100)}%</span>
      </div>
      <div style="display:flex;justify-content:space-between">
        <span style="color:rgba(255,255,255,0.4)">MOOD</span>
        <span>${Math.round(data.sentiment * 100)}%</span>
      </div>
    `
  }
}
