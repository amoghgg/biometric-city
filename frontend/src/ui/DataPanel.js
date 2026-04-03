// Updates the right-side data panel with city-wide averages

export class DataPanel {
  constructor() {
    this.bars = {
      aqi:       document.getElementById('bar-aqi'),
      crime:     document.getElementById('bar-crime'),
      crowd:     document.getElementById('bar-crowd'),
      noise:     document.getElementById('bar-noise'),
      sentiment: document.getElementById('bar-sentiment'),
    }
  }

  update(snapshot) {
    if (!snapshot?.districts) return
    const districts = Object.values(snapshot.districts)
    const avg = key => districts.reduce((s, d) => s + (d[key] || 0), 0) / districts.length

    this._setBar('aqi',       avg('aqi_normalized'))
    this._setBar('crime',     avg('crime'))
    this._setBar('crowd',     avg('crowd'))
    this._setBar('noise',     avg('noise'))
    this._setBar('sentiment', avg('sentiment'))
  }

  _setBar(key, value) {
    const el = this.bars[key]
    if (el) el.style.width = `${Math.round(value * 100)}%`
  }
}
