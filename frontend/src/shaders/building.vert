uniform float uTime;
uniform float uCrime;
uniform float uHeightMultiplier;
uniform float uLean;

varying vec2 vUv;
varying float vHeight;
varying float vFlicker;

float hash(float n) {
  return fract(sin(n) * 43758.5453);
}

void main() {
  vUv = uv;

  // Lean toward gentrifying direction (positive X axis)
  float leanAmount = uLean * 0.18;
  vec3 pos = position;

  // Apply lean: upper floors shift more than lower
  float normalizedHeight = (pos.y + 0.5); // 0 at base, 1 at top
  pos.x += normalizedHeight * leanAmount;

  // Crime-driven window flicker
  float flickerNoise = hash(floor(uTime * (2.0 + uCrime * 8.0) + position.x * 13.7 + position.z * 7.3));
  vFlicker = mix(0.85, 1.0, flickerNoise);

  // High crime = occasional total window blackout
  if (uCrime > 0.6 && flickerNoise < uCrime * 0.15) {
    vFlicker = 0.1;
  }

  vHeight = normalizedHeight;

  vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
  gl_Position = projectionMatrix * mvPosition;
}
