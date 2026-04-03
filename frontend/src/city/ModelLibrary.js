/**
 * ModelLibrary — loads Kenney Building Kit pieces and exposes them
 * for procedural building assembly via BuildingAssembler.js
 *
 * All .glb files live in:  frontend/public/models/parts/
 * (copied there from the Kenney Building Kit download)
 */

import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { assemble, FLOOR_H } from './BuildingAssembler.js'

// ── Pieces to preload ────────────────────────────────────────────────────────
// Each entry: logical name → path under /public
const PIECE_PATHS = {
  'wall':                        '/models/parts/wall.glb',
  'wall-corner':                 '/models/parts/wall-corner.glb',
  'wall-window-square':          '/models/parts/wall-window-square.glb',
  'wall-window-square-detailed': '/models/parts/wall-window-square-detailed.glb',
  'wall-window-wide-square':     '/models/parts/wall-window-wide-square.glb',
  'wall-half':                   '/models/parts/wall-half.glb',
  'floor':                       '/models/parts/floor.glb',
  'roof-flat-center':            '/models/parts/roof-flat-center.glb',
  'roof-flat-side':              '/models/parts/roof-flat-side.glb',
  'roof-flat-corner':            '/models/parts/roof-flat-corner.glb',
  'roof-flat-corner-inner':      '/models/parts/roof-flat-corner-inner.glb',
  'column':                      '/models/parts/column.glb',
  'detail-pipe':                 '/models/parts/detail-pipe.glb',
}

export class ModelLibrary {
  constructor() {
    this._loader = new GLTFLoader()
    this.pieces  = {}   // name → THREE.Group (centred, bottom at y=0)
    this.ready   = false
  }

  /**
   * Preload all building pieces.
   * GLTF loading is always async — this wraps each load in a Promise so we
   * can await everything before the city builds.
   */
  async load(onProgress) {
    const entries = Object.entries(PIECE_PATHS)
    let done = 0

    await Promise.allSettled(
      entries.map(([name, url]) =>
        new Promise(resolve => {
          this._loader.load(
            url,
            (gltf) => {
              // ── GLTF concept: normalise position so bottom sits at y=0 ─────
              const root = gltf.scene
              const box  = new THREE.Box3().setFromObject(root)
              const size = box.getSize(new THREE.Vector3())

              root.position.x -= (box.min.x + size.x / 2)
              root.position.z -= (box.min.z + size.z / 2)
              root.position.y -= box.min.y

              // Store the native piece dimensions for assembly grid calculations
              root.userData.nativeSize = size

              // Enable shadows on every mesh inside
              root.traverse(c => {
                if (c.isMesh) { c.castShadow = true; c.receiveShadow = true }
              })

              this.pieces[name] = root
              done++
              onProgress?.(done / entries.length)
              resolve()
            },
            null,
            (_err) => {
              console.warn(`[ModelLibrary] missing: ${url}`)
              done++
              onProgress?.(done / entries.length)
              resolve()
            }
          )
        })
      )
    )

    this.ready = Object.keys(this.pieces).length > 0
    console.log(`[ModelLibrary] ready — ${Object.keys(this.pieces).length}/${entries.length} pieces loaded`)
  }

  /**
   * Build a complete building GROUP from assembled pieces.
   *
   * targetHeight drives how many floors are stacked.
   * widthTiles / depthTiles come from the district's widthRange.
   */
  buildBuilding(opts) {
    if (!this.ready) return null

    const {
      targetHeight = 8,
      widthTiles   = 3,
      depthTiles   = 2,
      seed         = 1,
      wallColor    = new THREE.Color(0xd0c8b0),
      roofColor    = new THREE.Color(0x333333),
      style        = 'concrete',
      windowTint   = 'warm',
    } = opts

    // Clamp floors to a sensible range
    const floors = Math.max(1, Math.round(targetHeight / FLOOR_H))

    // Pass loaded pieces directly into the assembler
    const group = assemble(this.pieces, {
      widthTiles, depthTiles, floors, seed,
      wallColor, roofColor, style,
    })

    // Tag for tick() handling
    group.userData.isAssembled = true
    group.userData.baseFloors  = floors
    group.userData.nativeH     = floors * FLOOR_H

    // Store window materials for cheap emissive updates in tick()
    const winColor = windowTint === 'warm'
      ? new THREE.Color(1.0, 0.78, 0.38)
      : new THREE.Color(0.45, 0.70, 1.0)
    const emissiveMats = []
    group.traverse(c => {
      if (c.isMesh) {
        c.material = c.material.clone()
        c.material.emissive         = winColor.clone()
        c.material.emissiveIntensity = 0.6
        emissiveMats.push(c.material)
      }
    })
    group.userData.emissiveMats = emissiveMats

    return group
  }
}

// ── Module singleton ──────────────────────────────────────────────────────────
let _lib = null
export function setModelLibrary(instance) { _lib = instance }
export function getModelLibrary()         { return _lib }

// Keep PALETTE_MODEL_TYPE for reference (used by District for style picking)
export const PALETTE_MODEL_TYPE = {
  financial:   'glass',
  glass_blue:  'glass',
  glass_new:   'glass',
  limestone:   'concrete',
  brick_red:   'brick',
  brownstone:  'brick',
  warehouse:   'concrete',
  corporate:   'glass',
  modern_mn:   'glass',
  art_deco:    'concrete',
  colonial:    'concrete',
  bandra:      'brick',
  terracotta:  'brick',
  dharavi:     'brick',
  slum_bright: 'brick',
}
