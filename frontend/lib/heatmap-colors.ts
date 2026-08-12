/**
 * Perceptual heat scale: cool/low → warm/high.
 * Shared by densityToHeatBlobs(), HeatmapCanvas gradients, and HeatmapLegend.
 */
export const HEAT_SCALE_STOPS = [
  { t: 0.0, color: "#1a3a6e" },
  { t: 0.12, color: "#0055cc" },
  { t: 0.28, color: "#0099cc" },
  { t: 0.45, color: "#22bb88" },
  { t: 0.62, color: "#aacc22" },
  { t: 0.78, color: "#ffaa00" },
  { t: 0.92, color: "#ff5500" },
  { t: 1.0, color: "#ee1100" },
] as const;

function hexToRgb(hex: string): [number, number, number] {
  const normalized = hex.replace("#", "");
  return [
    parseInt(normalized.slice(0, 2), 16),
    parseInt(normalized.slice(2, 4), 16),
    parseInt(normalized.slice(4, 6), 16),
  ];
}

function rgbToHex(r: number, g: number, b: number): string {
  const channel = (value: number) =>
    Math.round(Math.max(0, Math.min(255, value)))
      .toString(16)
      .padStart(2, "0");
  return `#${channel(r)}${channel(g)}${channel(b)}`;
}

function lerpHex(a: string, b: string, t: number): string {
  const [ar, ag, ab] = hexToRgb(a);
  const [br, bg, bb] = hexToRgb(b);
  return rgbToHex(ar + (br - ar) * t, ag + (bg - ag) * t, ab + (bb - ab) * t);
}

/** Map normalized intensity 0–1 to an interpolated heat color. */
export function intensityToColor(intensity: number): string {
  const t = Math.max(0, Math.min(1, intensity));
  const stops = HEAT_SCALE_STOPS;

  if (t <= stops[0].t) return stops[0].color;
  const last = stops[stops.length - 1];
  if (t >= last.t) return last.color;

  for (let i = 1; i < stops.length; i++) {
    const upper = stops[i];
    const lower = stops[i - 1];
    if (t <= upper.t) {
      const span = upper.t - lower.t;
      const localT = span > 0 ? (t - lower.t) / span : 0;
      return lerpHex(lower.color, upper.color, localT);
    }
  }

  return last.color;
}

/** CSS linear-gradient for legend bars. */
export function heatGradientCss(direction: string = "to right"): string {
  const stops = HEAT_SCALE_STOPS.map(
    (stop) => `${stop.color} ${(stop.t * 100).toFixed(0)}%`,
  ).join(", ");
  return `linear-gradient(${direction}, ${stops})`;
}

export type DensityRange = {
  min: number;
  max: number;
};

/** Per-view min/max over non-zero cells so contrast spans the visible range. */
export function densityRange(density: number[][]): DensityRange | null {
  let min = Infinity;
  let max = 0;

  for (const row of density) {
    for (const value of row) {
      if (value <= 0) continue;
      if (value < min) min = value;
      if (value > max) max = value;
    }
  }

  if (!Number.isFinite(min) || max <= 0) return null;
  return { min, max };
}

/** Normalize a raw density cell to 0–1 using per-view min/max. */
export function densityToIntensity(
  value: number,
  range: DensityRange,
): number {
  if (value <= 0) return 0;
  if (range.max <= range.min) return 1;
  return Math.max(0, Math.min(1, (value - range.min) / (range.max - range.min)));
}
