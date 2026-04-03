/**
 * BuildingAssembler — procedural buildings from Kenney Building Kit parts
 *
 * How it works:
 *  1. ModelLibrary loads each wall/floor/roof piece as a cached GLTF template
 *  2. assemble() clones and arranges pieces into a complete multi-story building
 *  3. The result is a THREE.Group you can place anywhere in the scene
 *
 * Piece coordinate system (Kenney standard: 1-unit grid):
 *   Each wall tile   = 1 unit wide, 1 unit tall, ~0.1 units thick
 *   Each floor tile  = 1 unit wide, 1 unit deep, ~0.1 units tall
 *   Each corner tile = 1 unit × 1 unit (handles 90° joins)
 *   FLOOR_HEIGHT     = 1.0 world units per storey
 */

import * as THREE from 'three'

export const FLOOR_H = 1.0   // height of one storey (matches Kenney wall.glb native height)

// Pieces used by the assembler — keys match ModelLibrary piece names
const P = {
  WALL:        'wall',
  WALL_WIN:    'wall-window-square',
  WALL_WIN_D:  'wall-window-square-detailed',
  WALL_WIDE:   'wall-window-wide-square',
  CORNER:      'wall-corner',
  FLOOR:       'floor',
  ROOF_C:      'roof-flat-center',
  ROOF_S:      'roof-flat-side',
  ROOF_CRN:    'roof-flat-corner',
  ROOF_CRN_I:  'roof-flat-corner-inner',
  COLUMN:      'column',
  PIPE:        'detail-pipe',
}

function seededRng(seed) {
  let s = seed | 0
  return () => { s = (s * 16807 + 1) % 2147483647; return (s - 1) / 2147483646 }
}

/**
 * Clone a GLTF template piece, apply a color tint, and position it.
 * This is the core GLTF instancing pattern.
 */
function placePiece(template, x, y, z, rotY = 0, tint = null) {
  if (!template) return null
  const clone = template.clone(true)
  clone.position.set(x, y, z)
  clone.rotation.y = rotY
  if (tint) {
    clone.traverse(child => {
      if (child.isMesh) {
        child.material = child.material.clone()
        child.material.color.set(tint)
        child.castShadow    = true
        child.receiveShadow = true
      }
    })
  }
  return clone
}

/**
 * assemble() — build a complete multi-story building
 *
 * @param {object}  pieces       Map of piece name → THREE.Group (from ModelLibrary)
 * @param {object}  opts
 *   @param {number}  opts.widthTiles   Building width in tile units (2–6)
 *   @param {number}  opts.depthTiles   Building depth in tile units (2–4)
 *   @param {number}  opts.floors       Number of storeys (1–20)
 *   @param {number}  opts.seed         RNG seed for deterministic variety
 *   @param {THREE.Color} opts.wallColor   Facade colour
 *   @param {THREE.Color} opts.roofColor   Roof colour
 *   @param {string}  opts.style        'glass' | 'brick' | 'concrete'
 * @returns {THREE.Group}
 */
export function assemble(pieces, opts) {
  const {
    widthTiles = 3,
    depthTiles = 2,
    floors     = 4,
    seed       = 1,
    wallColor  = new THREE.Color(0xd0c8b0),
    roofColor  = new THREE.Color(0x404040),
    style      = 'concrete',
  } = opts

  const rng    = seededRng(seed)
  const group  = new THREE.Group()
  const W      = pieces[P.WALL]
  const WW     = pieces[P.WALL_WIN]   || pieces[P.WALL]
  const WWD    = pieces[P.WALL_WIN_D] || pieces[P.WALL_WIN] || pieces[P.WALL]
  const CRN    = pieces[P.CORNER]     || pieces[P.WALL]
  const FL     = pieces[P.FLOOR]
  const RC     = pieces[P.ROOF_C]
  const RS     = pieces[P.ROOF_S]
  const RCRN   = pieces[P.ROOF_CRN]
  const RCRNI  = pieces[P.ROOF_CRN_I]

  // ── Tint colours ───────────────────────────────────────────────────────────
  const wc = wallColor
  const rc2 = roofColor

  // ── Assemble floor by floor ────────────────────────────────────────────────
  for (let f = 0; f < floors; f++) {
    const y        = f * FLOOR_H
    const isGround = f === 0
    const isTop    = f === floors - 1

    // Decide window pattern for this floor (ground floor uses plain walls more)
    const winChance = isGround ? 0.2 : (style === 'glass' ? 0.85 : 0.55)

    // ── Front wall (z = 0), facing -Z ────────────────────────────────────────
    for (let x = 0; x < widthTiles; x++) {
      const isLeft  = x === 0
      const isRight = x === widthTiles - 1

      if (isLeft) {
        const p = placePiece(CRN, x, y, 0, 0, wc)
        if (p) group.add(p)
      } else if (isRight) {
        const p = placePiece(CRN, x, y, 0, Math.PI / 2, wc)
        if (p) group.add(p)
      } else {
        const useWin = rng() < winChance
        const tmpl   = useWin ? (style === 'glass' ? WWD : WW) : W
        const p = placePiece(tmpl, x, y, 0, 0, wc)
        if (p) group.add(p)
      }
    }

    // ── Back wall (z = depthTiles), facing +Z ─────────────────────────────────
    for (let x = 0; x < widthTiles; x++) {
      const isLeft  = x === 0
      const isRight = x === widthTiles - 1
      if (isLeft) {
        const p = placePiece(CRN, x, y, depthTiles, -Math.PI / 2, wc)
        if (p) group.add(p)
      } else if (isRight) {
        const p = placePiece(CRN, x, y, depthTiles, Math.PI, wc)
        if (p) group.add(p)
      } else {
        const useWin = rng() < winChance * 0.6  // back has fewer windows
        const tmpl   = useWin ? WW : W
        const p = placePiece(tmpl, x, y, depthTiles, Math.PI, wc)
        if (p) group.add(p)
      }
    }

    // ── Left wall (x = 0), facing -X ──────────────────────────────────────────
    for (let z = 1; z < depthTiles; z++) {
      const useWin = rng() < winChance * 0.4
      const tmpl   = useWin ? WW : W
      const p = placePiece(tmpl, 0, y, z, -Math.PI / 2, wc)
      if (p) group.add(p)
    }

    // ── Right wall (x = widthTiles), facing +X ────────────────────────────────
    for (let z = 1; z < depthTiles; z++) {
      const useWin = rng() < winChance * 0.4
      const tmpl   = useWin ? WW : W
      const p = placePiece(tmpl, widthTiles, y, z, Math.PI / 2, wc)
      if (p) group.add(p)
    }

    // ── Floor slab ─────────────────────────────────────────────────────────────
    if (FL && (isGround || style === 'concrete')) {
      for (let fx = 0; fx < widthTiles; fx++) {
        for (let fz = 0; fz < depthTiles; fz++) {
          const p = placePiece(FL, fx, y, fz, 0, rc2)
          if (p) group.add(p)
        }
      }
    }
  }

  // ── Roof ──────────────────────────────────────────────────────────────────
  const roofY = floors * FLOOR_H

  if (RC && RS && RCRN) {
    // corners
    if (RCRN) {
      group.add(placePiece(RCRN, 0,              roofY, 0,              0,              rc2))
      group.add(placePiece(RCRN, widthTiles - 1, roofY, 0,              Math.PI / 2,   rc2))
      group.add(placePiece(RCRN, 0,              roofY, depthTiles - 1, -Math.PI / 2,  rc2))
      group.add(placePiece(RCRN, widthTiles - 1, roofY, depthTiles - 1, Math.PI,       rc2))
    }
    // front/back edges
    for (let x = 1; x < widthTiles - 1; x++) {
      group.add(placePiece(RS, x, roofY, 0,              0,         rc2))
      group.add(placePiece(RS, x, roofY, depthTiles - 1, Math.PI,   rc2))
    }
    // left/right edges
    for (let z = 1; z < depthTiles - 1; z++) {
      group.add(placePiece(RS, 0,              roofY, z, -Math.PI / 2, rc2))
      group.add(placePiece(RS, widthTiles - 1, roofY, z,  Math.PI / 2, rc2))
    }
    // center fill
    for (let x = 1; x < widthTiles - 1; x++) {
      for (let z = 1; z < depthTiles - 1; z++) {
        group.add(placePiece(RC, x, roofY, z, 0, rc2))
      }
    }
  }

  // ── Rooftop detail: water tower stub or pipe for tall buildings ────────────
  if (floors > 5 && pieces[P.PIPE]) {
    const px = 0.5 + rng() * (widthTiles - 1)
    const pz = 0.5 + rng() * (depthTiles - 1)
    const pipe = placePiece(pieces[P.PIPE], px, roofY + 0.1, pz, rng() * Math.PI * 2, wc)
    if (pipe) group.add(pipe)
  }

  return group
}
