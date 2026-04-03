uniform float uTime;
uniform float uAqi;        // 0–1: air quality (0 = pristine, 1 = hazardous)
uniform float uCrime;      // 0–1
uniform float uSentiment;  // 0–1 (0 = despair, 1 = joy)
uniform float uNoise;      // 0–1
uniform vec3  uBaseColor;
uniform float uIsGlass;    // 1.0 for glass towers, 0.0 for masonry

varying vec2  vUv;
varying float vHeight;
varying float vFlicker;

float rand(vec2 co) {
  return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
  // ── Facade base color ──────────────────────────────────────────────────────
  vec3 cleanColor    = vec3(0.50, 0.72, 0.95);   // cool blue steel in clean air
  vec3 pollutedColor = vec3(0.88, 0.52, 0.18);   // dirty amber in smog
  vec3 bodyColor     = mix(cleanColor, pollutedColor, uAqi * 0.85);

  // Blend with the district base color
  bodyColor = mix(bodyColor, uBaseColor, 0.60);

  // Crime darkens lower floors (unsafe streets = lit windows higher up)
  float crimeShade = 1.0 - uCrime * 0.55 * (1.0 - vHeight);
  bodyColor *= crimeShade;

  // Glass: tinted reflective facade (slightly shifts toward sky color)
  if (uIsGlass > 0.5) {
    vec3 glassSheen = mix(vec3(0.45, 0.60, 0.90), vec3(0.60, 0.75, 0.95), vHeight);
    bodyColor = mix(bodyColor, glassSheen, 0.35);
  }

  // ── Window grid pattern ────────────────────────────────────────────────────
  // Two-frequency grid: major (floors) + minor (window panes within floor)
  vec2 wUv   = fract(vUv * vec2(5.0, 10.0));
  float wMask = step(0.12, wUv.x) * step(0.08, wUv.y)
              * step(wUv.x, 0.88) * step(wUv.y, 0.92);

  // Per-floor random occupancy — some floors lit, some dark
  float floorId  = floor(vUv.y * 10.0);
  float colId    = floor(vUv.x * 5.0);
  float occupied = rand(vec2(floorId, colId + 3.7));
  float isLit    = step(0.25, occupied);   // ~75% of windows lit

  // Window color: warm incandescent (sentiment high) or cold office blue (low)
  vec3 warmLight = vec3(1.00, 0.85, 0.45);   // warm-white incandescent
  vec3 coldLight = vec3(0.50, 0.72, 1.00);   // cool LED / fluorescent
  vec3 windowColor = mix(coldLight, warmLight, uSentiment);

  // Flicker from crime (occasional power outages)
  windowColor *= vFlicker * isLit;

  // Animated shimmer — noise / neon signs
  float shimmer = 1.0 + uNoise * 0.08 * sin(uTime * 3.5 + vUv.y * 25.0 + vUv.x * 12.0);
  bodyColor *= shimmer;

  // ── Combine facade + windows ───────────────────────────────────────────────
  float windowBlend = wMask * 0.75;
  vec3 finalColor = mix(bodyColor, windowColor, windowBlend);

  // ── Rooftop treatment ──────────────────────────────────────────────────────
  if (vHeight > 0.96) {
    // Plant / mechanical penthouse: dark with subtle teal accent
    vec3 roofColor = mix(bodyColor * 0.6, vec3(0.0, 0.85, 0.65), 0.55);
    float roofMix  = smoothstep(0.96, 1.0, vHeight);
    finalColor     = mix(finalColor, roofColor, roofMix);
  }

  // ── Specular highlight along facade (simulates sun reflection) ────────────
  float specLine = smoothstep(0.48, 0.50, vUv.x) * smoothstep(0.52, 0.50, vUv.x);
  finalColor += vec3(0.8, 0.9, 1.0) * specLine * uIsGlass * 0.18;

  gl_FragColor = vec4(finalColor, 1.0);
}
