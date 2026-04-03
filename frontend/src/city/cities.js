// NYC + Mumbai district configs with full geographic accuracy and visual identity
// Position: [x, z] in world space — negative z = south, positive z = north
// Based on real geographic research

export const CITY_PALETTES = {
  nyc: {
    // Financial District: dark steel + chrome — visible dark blue-grey
    financial:   ['#2a4a6a','#1e3a58','#3a5878','#304e6a','#253a52','#3c5a72'],
    // Midtown glass: actual sky-blue glass — bright, visible, reflective
    glass_blue:  ['#6ab0d8','#4a9ac8','#7ec0e8','#58aad4','#3a88bc','#82bce0'],
    // Limestone: warm cream — brighter so it pops
    limestone:   ['#e0cfa8','#d0bf98','#f0dfb8','#c8b888','#ddd0a8','#eadcb4'],
    // Brick red: actual visible red brick
    brick_red:   ['#c04828','#d45a38','#b03a20','#e06a48','#943018','#cc5030'],
    // Brownstone: warm medium brown — NOT dark
    brownstone:  ['#9a6840','#8a5830','#aa7848','#7a4820','#b08050','#906040'],
    // Warehouse: industrial grey-brown with warmth
    warehouse:   ['#7a6858','#8a7868','#6a5848','#9a8878','#5a4838','#887060'],
    // New glass: teal-blue modern
    glass_new:   ['#48a0c8','#3890ba','#5ab0d4','#2878a8','#68b8e0','#3898c0'],
  },
  mumbai: {
    // BKC corporate: visible dark teal-blue (not pure black)
    corporate:   ['#1a4060','#2a5272','#0e3050','#243858','#183448','#305470'],
    // Colaba colonial: bright colonial gold
    colonial:    ['#e8c050','#d8b040','#f0cc60','#c8a030','#dcba48','#f4d068'],
    // Dharavi: vivid rainbow — high saturation, actually bright
    dharavi:     ['#ff5533','#2288ee','#ffcc00','#33cc33','#ee2266','#ff8800','#8833dd','#ff4444','#00aacc','#ff3388'],
    // Terracotta: warm orange-brown, bright
    terracotta:  ['#e89050','#d88040','#f0a060','#c87030','#b86028','#eca060'],
    // Art Deco Marine Drive: ivory/cream white
    art_deco:    ['#f5f0e0','#e8e4d0','#fffaec','#f0ecdC','#ede8d8','#f8f4e4'],
    // Bandra: warm terracotta village
    bandra:      ['#e89858','#d88848','#f0a868','#c07838','#b86830','#eeaa70'],
    // Lower Parel modern: visible medium navy
    modern_mn:   ['#2a5070','#3a6080','#1c3e5c','#466278','#183650','#345878'],
    // Dharavi/Kurla bright slum colors: very vivid
    slum_bright: ['#ff4422','#22aaff','#ffdd00','#44dd44','#ff2277','#ff8822','#aa44ff','#00ddcc'],
  }
}

export const CITIES = {
  nyc: {
    name: 'NEW YORK CITY',
    cameraDefault: { x: 45, y: 60, z: 80 },
    skyColors: { zenith: '#060d28', mid: '#1848a0', horizon: '#4888d8', sun: '#ffd878' },
    waterColor: '#040e1c',
    islandColor: '#1a1a1c',
    roadColor:   '#0e0e10',
    groundExtent: [[-40, -70], [50, 70]], // [min x/z, max x/z]

    districts: {
      financial_district: {
        position: [-4, -52], size: [16, 16], buildingCount: 16,
        label: 'Financial District',
        heightRange: [12, 28], widthRange: [1.4, 2.6],
        palette: 'financial', windowTint: 'cool',
        hasWaterTowers: false, roofStyle: 'flat',
      },
      tribeca: {
        position: [-10, -37], size: [13, 13], buildingCount: 22,
        label: 'Tribeca',
        heightRange: [3, 8], widthRange: [0.9, 2.0],
        palette: 'brick_red', windowTint: 'warm',
        hasWaterTowers: true, roofStyle: 'flat',
      },
      midtown: {
        position: [0, 12], size: [22, 22], buildingCount: 40,
        label: 'Midtown',
        heightRange: [8, 30], widthRange: [1.2, 2.8],
        palette: 'glass_blue', windowTint: 'cool',
        hasWaterTowers: false, roofStyle: 'stepped',
      },
      lower_east: {
        position: [14, -28], size: [14, 14], buildingCount: 28,
        label: 'Lower East Side',
        heightRange: [2.5, 5], widthRange: [0.8, 1.6],
        palette: 'brick_red', windowTint: 'warm',
        hasWaterTowers: true, roofStyle: 'flat',
      },
      chelsea: {
        position: [-15, 4], size: [12, 14], buildingCount: 22,
        label: 'Chelsea',
        heightRange: [3, 9], widthRange: [1.2, 2.5],
        palette: 'warehouse', windowTint: 'warm',
        hasWaterTowers: true, roofStyle: 'flat',
      },
      upper_west: {
        position: [-16, 30], size: [14, 18], buildingCount: 26,
        label: 'Upper West Side',
        heightRange: [6, 14], widthRange: [1.0, 2.2],
        palette: 'limestone', windowTint: 'warm',
        hasWaterTowers: true, roofStyle: 'flat',
      },
      harlem: {
        position: [-5, 46], size: [18, 18], buildingCount: 32,
        label: 'Harlem',
        heightRange: [2, 5], widthRange: [0.9, 1.8],
        palette: 'brownstone', windowTint: 'warm',
        hasWaterTowers: true, roofStyle: 'flat',
      },
      brooklyn: {
        position: [32, -50], size: [24, 22], buildingCount: 36,
        label: 'Brooklyn',
        heightRange: [2.5, 12], widthRange: [0.9, 2.5],
        palette: 'brick_red', windowTint: 'warm',
        hasWaterTowers: true, roofStyle: 'flat',
      },
      williamsburg: {
        position: [38, -28], size: [14, 14], buildingCount: 24,
        label: 'Williamsburg',
        heightRange: [3, 16], widthRange: [1.0, 2.5],
        palette: 'warehouse', windowTint: 'warm',
        hasWaterTowers: true, roofStyle: 'flat',
      },
      queens: {
        position: [58, 8], size: [22, 22], buildingCount: 30,
        label: 'Queens',
        heightRange: [3, 9], widthRange: [0.9, 2.0],
        palette: 'limestone', windowTint: 'warm',
        hasWaterTowers: true, roofStyle: 'flat',
      },
      bronx: {
        position: [12, 62], size: [20, 18], buildingCount: 28,
        label: 'The Bronx',
        heightRange: [3, 10], widthRange: [1.0, 2.2],
        palette: 'brownstone', windowTint: 'warm',
        hasWaterTowers: true, roofStyle: 'flat',
      },
      flushing: {
        position: [72, 22], size: [16, 16], buildingCount: 22,
        label: 'Flushing',
        heightRange: [2, 8], widthRange: [0.9, 1.8],
        palette: 'limestone', windowTint: 'warm',
        hasWaterTowers: false, roofStyle: 'flat',
      },
    }
  },

  mumbai: {
    name: 'MUMBAI',
    cameraDefault: { x: 35, y: 55, z: 75 },
    skyColors: { zenith: '#100820', mid: '#3828a0', horizon: '#c07030', sun: '#ffa030' },
    waterColor: '#030c16',
    islandColor: '#1a1810',
    roadColor:   '#100e0c',
    groundExtent: [[-50, -65], [55, 68]],

    districts: {
      colaba: {
        position: [-18, -54], size: [14, 14], buildingCount: 20,
        label: 'Colaba',
        heightRange: [2, 5], widthRange: [1.0, 2.5],
        palette: 'colonial', windowTint: 'warm',
        hasChhajjas: true, roofStyle: 'flat',
      },
      marine_drive: {
        position: [-26, -38], size: [10, 18], buildingCount: 22,
        label: 'Marine Drive',
        heightRange: [5, 10], widthRange: [1.5, 3.0],
        palette: 'art_deco', windowTint: 'warm',
        hasChhajjas: true, roofStyle: 'flat',
      },
      bkc: {
        position: [4, 0], size: [18, 16], buildingCount: 24,
        label: 'BKC',
        heightRange: [12, 24], widthRange: [1.5, 2.8],
        palette: 'corporate', windowTint: 'cool',
        hasChhajjas: false, roofStyle: 'flat',
      },
      bandra: {
        position: [-24, -16], size: [16, 14], buildingCount: 30,
        label: 'Bandra',
        heightRange: [2, 18], widthRange: [0.9, 2.5],
        palette: 'bandra', windowTint: 'warm',
        hasChhajjas: true, roofStyle: 'mixed',
      },
      dharavi: {
        position: [8, -16], size: [12, 10], buildingCount: 55,
        label: 'Dharavi',
        heightRange: [1, 3], widthRange: [0.5, 1.2],
        palette: 'dharavi', windowTint: 'warm',
        hasChhajjas: true, roofStyle: 'flat',
      },
      dadar: {
        position: [-12, -8], size: [14, 12], buildingCount: 32,
        label: 'Dadar',
        heightRange: [3, 8], widthRange: [1.0, 2.0],
        palette: 'terracotta', windowTint: 'warm',
        hasChhajjas: true, roofStyle: 'flat',
      },
      lower_parel: {
        position: [-10, 6], size: [14, 12], buildingCount: 22,
        label: 'Lower Parel',
        heightRange: [4, 22], widthRange: [1.2, 3.0],
        palette: 'modern_mn', windowTint: 'cool',
        hasChhajjas: false, roofStyle: 'flat',
      },
      kurla: {
        position: [26, 8], size: [16, 14], buildingCount: 32,
        label: 'Kurla',
        heightRange: [3, 9], widthRange: [0.9, 2.0],
        palette: 'slum_bright', windowTint: 'warm',
        hasChhajjas: true, roofStyle: 'flat',
      },
      andheri: {
        position: [12, 38], size: [22, 20], buildingCount: 36,
        label: 'Andheri',
        heightRange: [4, 14], widthRange: [1.0, 2.5],
        palette: 'terracotta', windowTint: 'warm',
        hasChhajjas: true, roofStyle: 'flat',
      },
      borivali: {
        position: [18, 60], size: [18, 16], buildingCount: 26,
        label: 'Borivali',
        heightRange: [3, 10], widthRange: [1.0, 2.2],
        palette: 'terracotta', windowTint: 'warm',
        hasChhajjas: true, roofStyle: 'flat',
      },
      thane: {
        position: [48, 48], size: [20, 18], buildingCount: 24,
        label: 'Thane',
        heightRange: [3, 12], widthRange: [1.0, 2.5],
        palette: 'terracotta', windowTint: 'warm',
        hasChhajjas: true, roofStyle: 'flat',
      },
    }
  }
}
