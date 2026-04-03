import * as THREE from 'three'

function seededRng(seed) {
  let s = seed
  return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646 }
}

export class SkyDome {
  constructor(scene) {
    this.scene = scene
    this._build()
    this._buildStars()
  }

  _build() {
    const geo = new THREE.SphereGeometry(480, 48, 24)
    geo.scale(-1, 1, 1)

    this.mat = new THREE.ShaderMaterial({
      side: THREE.FrontSide,
      depthWrite: false,
      uniforms: {
        uZenith:        { value: new THREE.Color('#0a1535') },
        uUpper:         { value: new THREE.Color('#1a3060') },
        uMid:           { value: new THREE.Color('#3060a0') },
        uHorizon:       { value: new THREE.Color('#6090c8') },
        uHorizonGlow:   { value: new THREE.Color('#f0a060') },
        uSunDir:        { value: new THREE.Vector3(0.4, 0.6, 0.6).normalize() },
        uSunColor:      { value: new THREE.Color('#ffd080') },
        uTime:          { value: 0 },
        uStarBrightness:{ value: 0.8 },
      },
      vertexShader: `
        varying vec3 vWorldPos;
        void main() {
          vWorldPos = position;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform vec3  uZenith;
        uniform vec3  uUpper;
        uniform vec3  uMid;
        uniform vec3  uHorizon;
        uniform vec3  uHorizonGlow;
        uniform vec3  uSunDir;
        uniform vec3  uSunColor;
        uniform float uTime;
        uniform float uStarBrightness;
        varying vec3  vWorldPos;

        // Pseudo-random for stars
        float hash(vec2 p) {
          return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
        }
        float hash3(vec3 p) {
          return fract(sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453);
        }

        float starField(vec3 dir) {
          // Map to spherical grid cells
          float phi   = atan(dir.z, dir.x);
          float theta = asin(clamp(dir.y, -1.0, 1.0));
          vec2  cell  = floor(vec2(phi, theta) * 60.0);
          float rng   = hash(cell);
          // Only show ~3% of cells as stars
          if (rng < 0.97) return 0.0;
          vec2  frac  = fract(vec2(phi, theta) * 60.0) - 0.5;
          float d     = length(frac);
          float bright = (rng - 0.97) / 0.03;            // 0–1
          float twinkle = 0.75 + 0.25 * sin(uTime * (2.0 + rng * 4.0) + rng * 6.28);
          return smoothstep(0.22, 0.0, d) * bright * twinkle;
        }

        void main() {
          vec3  dir  = normalize(vWorldPos);
          float elev = dir.y;

          // 4-band sky gradient for cinematic depth
          vec3 sky;
          if (elev > 0.55) {
            sky = mix(uUpper, uZenith, (elev - 0.55) / 0.45);
          } else if (elev > 0.15) {
            sky = mix(uMid, uUpper, (elev - 0.15) / 0.40);
          } else if (elev > 0.0) {
            sky = mix(uHorizon, uMid, elev / 0.15);
          } else {
            sky = mix(uHorizon, vec3(0.025, 0.018, 0.012), min(-elev * 6.0, 1.0));
          }

          // Warm horizon glow band (sunset/city light scatter)
          float hBand = exp(-abs(elev - 0.02) * 10.0);
          sky = mix(sky, uHorizonGlow, hBand * 0.28);

          // Atmospheric haze: gentle back-scatter near horizon
          float haze = smoothstep(0.18, 0.0, abs(elev)) * 0.12;
          sky += uSunColor * haze;

          // Sun disk + multi-ring corona
          vec3  sunN    = normalize(uSunDir);
          float sunDot  = dot(dir, sunN);
          float sunCore = smoothstep(0.9997, 1.0,    sunDot);           // tight disk
          float corona1 = smoothstep(0.9985, 0.9997, sunDot) * 0.55;   // inner corona
          float corona2 = smoothstep(0.990,  0.9985, sunDot) * 0.22;   // mid corona
          float corona3 = smoothstep(0.960,  0.990,  sunDot) * 0.08;   // outer glow
          float corona4 = smoothstep(0.88,   0.960,  sunDot) * 0.025;  // very wide diffuse
          sky += uSunColor * (sunCore * 5.0 + corona1 + corona2 + corona3 + corona4);

          // Stars — fade out as sky brightens (daytime suppresses them)
          float skyLum = dot(sky, vec3(0.299, 0.587, 0.114));
          float starMask = uStarBrightness * clamp(1.0 - skyLum * 2.8, 0.0, 1.0);
          if (elev > 0.0 && starMask > 0.001) {
            sky += vec3(0.88, 0.92, 1.0) * starField(dir) * starMask;
          }

          gl_FragColor = vec4(sky, 1.0);
        }
      `,
    })

    this.mesh = new THREE.Mesh(geo, this.mat)
    this.mesh.renderOrder = -1
    this.scene.add(this.mesh)
  }

  _buildStars() {
    // Bright star billboard layer (separate from shader micro-stars)
    // These catch bloom and look like real stars
    const rng   = seededRng(777)
    const count = 900
    const positions = new Float32Array(count * 3)
    const colors    = new Float32Array(count * 3)
    const sizes     = new Float32Array(count)

    for (let i = 0; i < count; i++) {
      // Random point on upper hemisphere
      const theta = rng() * Math.PI * 2
      const phi   = Math.acos(rng() * 0.78 + 0.07) // avoid very close to horizon
      const r     = 465
      positions[i * 3]     = r * Math.sin(phi) * Math.cos(theta)
      positions[i * 3 + 1] = r * Math.cos(phi)
      positions[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta)

      // Star color variety: blue-white, white, warm yellow-white
      const t = rng()
      if (t < 0.3) {
        // Blue-white (hot star)
        colors[i * 3] = 0.80; colors[i * 3 + 1] = 0.88; colors[i * 3 + 2] = 1.00
      } else if (t < 0.7) {
        // Pure white
        colors[i * 3] = 0.95; colors[i * 3 + 1] = 0.95; colors[i * 3 + 2] = 0.98
      } else {
        // Warm yellow-white (cooler star)
        colors[i * 3] = 1.00; colors[i * 3 + 1] = 0.92; colors[i * 3 + 2] = 0.75
      }

      // Varied sizes — most tiny, a few bright
      sizes[i] = rng() < 0.05 ? 1.8 + rng() * 1.4 : 0.5 + rng() * 0.9
    }

    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geo.setAttribute('color',    new THREE.BufferAttribute(colors, 3))
    geo.setAttribute('size',     new THREE.BufferAttribute(sizes, 1))

    const mat = new THREE.PointsMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.90,
      sizeAttenuation: true,
      depthWrite: false,
      size: 0.9,
    })

    this.stars     = new THREE.Points(geo, mat)
    this.stars.renderOrder = -2
    this.starsMat  = mat
    this.scene.add(this.stars)
  }

  setCity(cityConfig) {
    const { skyColors } = cityConfig
    this.mat.uniforms.uZenith.value.set(skyColors.zenith)
    this.mat.uniforms.uMid.value.set(skyColors.mid)
    this.mat.uniforms.uHorizon.value.set(skyColors.horizon)
    this.mat.uniforms.uSunColor.value.set(skyColors.sun)

    // Derive upper color (between zenith and mid)
    const z = new THREE.Color(skyColors.zenith)
    const m = new THREE.Color(skyColors.mid)
    this.mat.uniforms.uUpper.value.lerpColors(z, m, 0.45)

    // Horizon glow: warm for Mumbai sunset, cooler for NYC
    if (cityConfig.name === 'MUMBAI') {
      this.mat.uniforms.uHorizonGlow.value.set('#f08030')
      this.mat.uniforms.uStarBrightness.value = 1.0
    } else {
      this.mat.uniforms.uHorizonGlow.value.set('#c07840')
      this.mat.uniforms.uStarBrightness.value = 0.8
    }
  }

  tick(time) {
    this.mat.uniforms.uTime.value = time
  }

  dispose() {
    this.mesh.geometry.dispose()
    this.mat.dispose()
    this.scene.remove(this.mesh)
    if (this.stars) {
      this.stars.geometry.dispose()
      this.starsMat.dispose()
      this.scene.remove(this.stars)
    }
  }
}
