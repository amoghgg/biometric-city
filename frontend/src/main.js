import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js'
import { CITIES } from './city/cities.js'
import { CityGrid } from './city/CityGrid.js'
import { Landmarks } from './city/Landmarks.js'
import { ModelLibrary, setModelLibrary } from './city/ModelLibrary.js'
import { SkyDome } from './environment/SkyDome.js'
import { Ocean } from './environment/Ocean.js'
import { Clouds } from './environment/Clouds.js'
import { Particles } from './effects/Particles.js'
import { CrimePulse } from './effects/CrimePulse.js'
import { Atmosphere } from './effects/Atmosphere.js'
import { CitySwitch } from './ui/CitySwitch.js'
import { DataPanel } from './ui/DataPanel.js'
import { Tooltip } from './ui/Tooltip.js'
import { CitySocket } from './ws.js'

// ─── Scene Setup ────────────────────────────────────────────────────────────

const container = document.getElementById('canvas-container')
const renderer  = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' })
renderer.setPixelRatio(Math.min(devicePixelRatio, 2))
renderer.setSize(window.innerWidth, window.innerHeight)
renderer.shadowMap.enabled = true
renderer.shadowMap.type = THREE.PCFSoftShadowMap
renderer.toneMapping = THREE.ACESFilmicToneMapping
renderer.toneMappingExposure = 0.75
renderer.outputColorSpace = THREE.SRGBColorSpace
container.appendChild(renderer.domElement)

const scene = new THREE.Scene()
// No scene.background — SkyDome covers it

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.5, 1200)
camera.position.set(45, 60, 80)
camera.lookAt(0, 0, 0)

const controls = new OrbitControls(camera, renderer.domElement)
controls.enableDamping = true
controls.dampingFactor = 0.06
controls.maxPolarAngle = Math.PI / 2.08
controls.minDistance = 18
controls.maxDistance = 320
controls.target.set(0, 0, 0)

// ─── Lighting ────────────────────────────────────────────────────────────────

// Sun — directional with soft shadows
const sun = new THREE.DirectionalLight(0xfff5e0, 1.4)
sun.position.set(60, 120, 80)
sun.castShadow = true
sun.shadow.mapSize.set(2048, 2048)
sun.shadow.camera.near = 1
sun.shadow.camera.far = 400
sun.shadow.camera.left = -120
sun.shadow.camera.right = 120
sun.shadow.camera.top = 120
sun.shadow.camera.bottom = -120
sun.shadow.bias = -0.0003
scene.add(sun)

// Sky ambient — subtle fill
const ambient = new THREE.AmbientLight(0x4060a0, 0.6)
scene.add(ambient)

// Hemisphere — warm ground / cool sky
const hemi = new THREE.HemisphereLight(0x6088c0, 0x4a3020, 0.5)
scene.add(hemi)

// Secondary fill from opposite side
const fillLight = new THREE.DirectionalLight(0x304080, 0.4)
fillLight.position.set(-40, 60, -60)
scene.add(fillLight)

// ─── Post-Processing ─────────────────────────────────────────────────────────

const composer = new EffectComposer(renderer)
composer.addPass(new RenderPass(scene, camera))

const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  0.55,   // strength — subtle city glow
  0.45,   // radius   — tight spread
  0.75    // threshold — only the brightest spots bloom
)
composer.addPass(bloomPass)
composer.addPass(new OutputPass())

// ─── City Atmosphere Lights ───────────────────────────────────────────────────

// Warm upward light pollution from streets (subtle orange tint on building bases)
const cityUpGlow = new THREE.PointLight(0xff7722, 2.5, 160, 1.8)
cityUpGlow.position.set(0, 1.5, 0)
scene.add(cityUpGlow)

// Secondary warm node — creates depth / multiple light zones
const cityUpGlow2 = new THREE.PointLight(0xffaa44, 1.2, 100, 2.0)
cityUpGlow2.position.set(18, 1.5, 18)
scene.add(cityUpGlow2)

const cityUpGlow3 = new THREE.PointLight(0xff9933, 1.0, 90, 2.0)
cityUpGlow3.position.set(-20, 1.5, -15)
scene.add(cityUpGlow3)

// ─── Environment Systems ─────────────────────────────────────────────────────

const skyDome  = new SkyDome(scene)
const ocean    = new Ocean(scene)
const clouds   = new Clouds(scene)

// ─── City Systems ────────────────────────────────────────────────────────────

const cityGrid  = new CityGrid(scene)
const landmarks = new Landmarks(scene)

const particles  = new Particles(scene)
const crimePulse = new CrimePulse(scene)
const atmosphere = new Atmosphere(scene)
const dataPanel  = new DataPanel()
const tooltip    = new Tooltip()

let currentCity     = 'nyc'
let currentSnapshot = null
let socket          = null

// ─── Environment city update ─────────────────────────────────────────────────

function applyEnvCity(cityKey) {
  const config = CITIES[cityKey]
  skyDome.setCity(config)
  ocean.setCity(config)
  clouds.setCity(config)

  // Swap sun color + bloom per city
  if (cityKey === 'mumbai') {
    sun.color.set(0xffcc80)
    sun.intensity = 1.8
    ambient.color.set(0x906838)
    ambient.intensity = 0.7
    hemi.color.set(0xc09050)
    fillLight.color.set(0x603018)
    cityUpGlow.color.set(0xff9933)
    cityUpGlow2.color.set(0xffcc66)
    cityUpGlow3.color.set(0xff8822)
    bloomPass.strength = 0.65
    bloomPass.threshold = 0.72
  } else {
    sun.color.set(0xfff5e0)
    sun.intensity = 1.4
    ambient.color.set(0x4060a0)
    ambient.intensity = 0.6
    hemi.color.set(0x6088c0)
    fillLight.color.set(0x304080)
    cityUpGlow.color.set(0xff7722)
    cityUpGlow2.color.set(0xffaa44)
    cityUpGlow3.color.set(0xff9933)
    bloomPass.strength = 0.55
    bloomPass.threshold = 0.75
  }
}

// ─── Landmarks ───────────────────────────────────────────────────────────────

function loadLandmarks(cityKey) {
  landmarks.loadCity(cityKey)
}

// ─── City Switch ─────────────────────────────────────────────────────────────

const citySwitch = new CitySwitch(camera, cityGrid, (newCity) => {
  currentCity = newCity
  applyEnvCity(newCity)
  loadLandmarks(newCity)
  socket?.destroy()
  socket = new CitySocket(newCity, handleSnapshot)
})

// ─── Snapshot Handler ────────────────────────────────────────────────────────

function handleSnapshot(snapshot) {
  currentSnapshot = snapshot
  cityGrid.applySnapshot(snapshot)
  dataPanel.update(snapshot)

  const districts = Object.values(snapshot.districts)
  const avgAqi       = districts.reduce((s, d) => s + d.aqi_normalized, 0) / districts.length
  const avgSentiment = districts.reduce((s, d) => s + d.sentiment, 0) / districts.length
  const avgCrowd     = districts.reduce((s, d) => s + d.crowd, 0) / districts.length
  atmosphere.update(avgAqi, avgSentiment)
  particles.setCrowd(avgCrowd)
}

// ─── Raycasting for Tooltip ──────────────────────────────────────────────────

const raycaster = new THREE.Raycaster()
const mouse     = new THREE.Vector2()

window.addEventListener('mousemove', (e) => {
  mouse.x =  (e.clientX / window.innerWidth)  * 2 - 1
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1

  raycaster.setFromCamera(mouse, camera)
  const hit = cityGrid.getDistrictAtRay(raycaster)

  if (hit && currentSnapshot) {
    const data = currentSnapshot.districts[hit.key]
    if (data) tooltip.show(hit.key, data, currentCity, e.clientX, e.clientY)
  } else {
    tooltip.hide()
  }
})

// ─── Init ────────────────────────────────────────────────────────────────────

async function init() {
  // ── Load GLTF models first ─────────────────────────────────────────────────
  // This is the GLTF pipeline: create library → load all .glb files → set singleton
  // District.js reads the singleton via getModelLibrary() when building the city.
  const loadingText = document.getElementById('loading-text')
  const modelLib = new ModelLibrary()
  if (loadingText) loadingText.textContent = 'Loading 3D models...'
  await modelLib.load((p) => {
    if (loadingText) loadingText.textContent = `Loading models… ${Math.round(p * 100)}%`
  })
  setModelLibrary(modelLib)
  if (loadingText) loadingText.textContent = 'Building city...'

  await cityGrid.loadCity('nyc')
  applyEnvCity('nyc')
  loadLandmarks('nyc')

  try {
    const resp = await fetch(`/snapshot/nyc`)
    if (resp.ok) {
      const snap = await resp.json()
      handleSnapshot(snap)
    }
  } catch (_) {}

  socket = new CitySocket('nyc', handleSnapshot)

  const loading = document.getElementById('loading')
  loading.style.opacity = '0'
  setTimeout(() => { loading.style.display = 'none' }, 800)
}

// ─── Render Loop ──────────────────────────────────────────────────────────────

const clock = new THREE.Clock()
let lastPulseTime = 0

function animate() {
  requestAnimationFrame(animate)
  const elapsed = clock.getElapsedTime()
  const delta   = clock.getDelta()

  controls.update()
  skyDome.tick(elapsed)
  ocean.tick(elapsed)
  clouds.tick(elapsed)
  cityGrid.tick(elapsed)
  particles.tick()
  crimePulse.tick(delta)

  if (elapsed - lastPulseTime > 1.2 && currentSnapshot) {
    const cityConfig = CITIES[currentCity]
    crimePulse.autoTrigger(currentSnapshot.districts, cityConfig)
    lastPulseTime = elapsed
  }

  composer.render()
}

// ─── Resize ──────────────────────────────────────────────────────────────────

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
  composer.setSize(window.innerWidth, window.innerHeight)
  bloomPass.resolution.set(window.innerWidth, window.innerHeight)
})

// ─── Go ───────────────────────────────────────────────────────────────────────

init().then(animate)
