import { describe, expect, it } from "vitest";
import {
  densityRange,
  densityToIntensity,
  heatGradientCss,
  intensityToColor,
} from "./heatmap-colors";
import { densityToHeatBlobs } from "./api/mappers";

describe("heatmap-colors", () => {
  it("maps low intensity to cool colors and high to warm", () => {
    expect(intensityToColor(0)).toBe("#1a3a6e");
    expect(intensityToColor(1)).toBe("#ee1100");
    const mid = intensityToColor(0.5);
    expect(mid).toMatch(/^#[0-9a-f]{6}$/i);
    expect(mid).not.toBe(intensityToColor(0));
    expect(mid).not.toBe(intensityToColor(1));
  });

  it("normalizes per-view non-zero min/max", () => {
    const density = [
      [0, 10, 20],
      [0, 30, 120],
    ];
    const range = densityRange(density);
    expect(range).toEqual({ min: 10, max: 120 });
    expect(densityToIntensity(10, range!)).toBe(0);
    expect(densityToIntensity(120, range!)).toBe(1);
    expect(densityToIntensity(65, range!)).toBeCloseTo(0.5, 5);
  });

  it("exports a multi-stop CSS gradient", () => {
    const css = heatGradientCss();
    expect(css).toContain("linear-gradient");
    expect(css).toContain("#1a3a6e");
    expect(css).toContain("#ee1100");
  });
});

describe("densityToHeatBlobs", () => {
  it("includes all non-zero cells with distinct colors across the range", () => {
    const density = [
      [0, 10, 0],
      [20, 60, 120],
    ];
    const blobs = densityToHeatBlobs(density);
    expect(blobs).toHaveLength(4);

    const colors = new Set(blobs.map((blob) => blob.color));
    expect(colors.size).toBeGreaterThan(1);

    const hottest = blobs.find((blob) => blob.intensity === 1);
    const coolest = blobs.reduce((min, blob) =>
      blob.intensity < min.intensity ? blob : min,
    );
    expect(hottest?.color).toBe(intensityToColor(1));
    expect(coolest.color).toBe(intensityToColor(0));
  });

  it("returns empty array when all values are zero", () => {
    expect(densityToHeatBlobs([[0, 0], [0, 0]])).toEqual([]);
  });
});
