import * as THREE from 'three'

export class Ocean {
  constructor(scene) {
    this.scene = scene
    this._build()
  }

  _build() {
    // Higher vertex count → smoother, more detailed waves
    const geo = new THREE.PlaneGeometry(700, 700, 120, 120)

    this.mat = new THREE.ShaderMaterial({
      transparent: true,
      side: THREE.FrontSide,
      uniforms: {
        uTime:         { value: 0 },
        uDeepColor:    { value: new THREE.Color(0x020c1a) },
        uShallowColor: { value: new THREE.Color(0x082030) },
        uFoamColor:    { value: new THREE.Color(0x9acce0) },
        uSkyColor:     { value: new THREE.Color(0x3060a0) },  // reflected sky
        uSunDir:       { value: new THREE.Vector3(0.4, 0.8, 0.4).normalize() },
        uSunColor:     { value: new THREE.Color(0xffd080) },
      },
      vertexShader: `
        uniform float uTime;
        varying vec2  vUv;
        varying float vHeight;
        varying vec3  vNormal;
        varying vec3  vWorldPos;

        float wave(vec2 pos, float freq, float speed, float amp, float dir) {
          float k = freq;
          float c = speed;
          float a = amp;
          float ang = dir;
          return sin(pos.x * k * cos(ang) + pos.y * k * sin(ang) + uTime * c) * a;
        }

        float dwave_dx(vec2 pos, float freq, float speed, float amp, float dir) {
          return cos(pos.x * freq * cos(dir) + pos.y * freq * sin(dir) + uTime * speed)
                 * amp * freq * cos(dir);
        }
        float dwave_dz(vec2 pos, float freq, float speed, float amp, float dir) {
          return cos(pos.x * freq * cos(dir) + pos.y * freq * sin(dir) + uTime * speed)
                 * amp * freq * sin(dir);
        }

        void main() {
          vUv = uv;
          vec3 pos = position;

          // 5-layer ocean waves (different scales and directions)
          float w1 = wave(pos.xz, 0.07, 0.55, 0.28, 0.00);
          float w2 = wave(pos.xz, 0.13, 0.90, 0.14, 0.90);
          float w3 = wave(pos.xz, 0.22, 1.30, 0.07, 2.10);
          float w4 = wave(pos.xz, 0.05, 0.38, 0.32, 3.90);
          float w5 = wave(pos.xz, 0.34, 1.80, 0.04, 1.40);
          pos.y += w1 + w2 + w3 + w4 + w5;
          vHeight = pos.y;

          // Normal from partial derivatives
          float dx = dwave_dx(pos.xz, 0.07, 0.55, 0.28, 0.00)
                   + dwave_dx(pos.xz, 0.13, 0.90, 0.14, 0.90)
                   + dwave_dx(pos.xz, 0.05, 0.38, 0.32, 3.90);
          float dz = dwave_dz(pos.xz, 0.07, 0.55, 0.28, 0.00)
                   + dwave_dz(pos.xz, 0.13, 0.90, 0.14, 0.90)
                   + dwave_dz(pos.xz, 0.05, 0.38, 0.32, 3.90);
          vNormal = normalize(vec3(-dx, 1.0, -dz));

          vWorldPos = pos;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
        }
      `,
      fragmentShader: `
        uniform float uTime;
        uniform vec3  uDeepColor;
        uniform vec3  uShallowColor;
        uniform vec3  uFoamColor;
        uniform vec3  uSkyColor;
        uniform vec3  uSunDir;
        uniform vec3  uSunColor;
        varying vec2  vUv;
        varying float vHeight;
        varying vec3  vNormal;
        varying vec3  vWorldPos;

        void main() {
          // Base water depth color
          vec3 water = mix(uDeepColor, uShallowColor, clamp(vHeight * 1.2 + 0.5, 0.0, 1.0));

          // ── Fresnel reflectivity ──────────────────────────────────────────────
          // Approximate: more reflective at grazing angles (looking across water)
          vec3  camDir  = normalize(vec3(0.35, 0.85, 0.40));  // approx camera-to-surface
          float cosAng  = max(dot(normalize(vNormal), camDir), 0.0);
          float fresnel = pow(1.0 - cosAng, 3.5);
          fresnel       = mix(0.02, 0.85, fresnel);

          // Sky reflection color blended in by fresnel
          water = mix(water, uSkyColor * 0.55, fresnel * 0.50);

          // ── Sun specular ──────────────────────────────────────────────────────
          vec3  halfDir = normalize(uSunDir + camDir);
          float spec    = pow(max(dot(vNormal, halfDir), 0.0), 120.0);
          // Broader soft glow around specular
          float specSoft = pow(max(dot(vNormal, halfDir), 0.0), 30.0) * 0.12;
          water += uSunColor * (spec * 0.85 + specSoft);

          // ── Micro-shimmer (surface detail) ────────────────────────────────────
          float shimmer = 0.5 + 0.5 * sin(vUv.x * 180.0 + uTime * 2.5)
                                     * cos(vUv.y * 140.0 + uTime * 1.8);
          water += vec3(0.06, 0.14, 0.24) * shimmer * 0.08;

          // ── Foam at wave crests ───────────────────────────────────────────────
          float foam = smoothstep(0.22, 0.42, vHeight);
          water = mix(water, uFoamColor, foam * 0.18);

          // ── Edge foam (slightly brighter along shore) ─────────────────────────
          float edgeDist = length(vWorldPos.xz) / 340.0;
          float edgeFoam = smoothstep(0.88, 1.0, edgeDist) * 0.12;
          water = mix(water, uFoamColor * 0.6, edgeFoam);

          gl_FragColor = vec4(water, 0.97);
        }
      `,
    })

    this.mesh = new THREE.Mesh(geo, this.mat)
    this.mesh.rotation.x = -Math.PI / 2
    this.mesh.position.y = -0.8
    this.mesh.receiveShadow = false
    this.scene.add(this.mesh)
  }

  setCity(cityConfig) {
    const { skyColors } = cityConfig
    if (cityConfig.name === 'MUMBAI') {
      this.mat.uniforms.uDeepColor.value.set(0x020c14)
      this.mat.uniforms.uShallowColor.value.set(0x06182a)
      this.mat.uniforms.uSkyColor.value.set(skyColors.horizon)
      this.mat.uniforms.uSunColor.value.set(0xffa040)
    } else {
      this.mat.uniforms.uDeepColor.value.set(0x020e1c)
      this.mat.uniforms.uShallowColor.value.set(0x082035)
      this.mat.uniforms.uSkyColor.value.set(skyColors.horizon)
      this.mat.uniforms.uSunColor.value.set(0xffd080)
    }
  }

  tick(time) {
    this.mat.uniforms.uTime.value = time
  }

  dispose() {
    this.mesh.geometry.dispose()
    this.mat.dispose()
    this.scene.remove(this.mesh)
  }
}
