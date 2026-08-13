import { describe, expect, it } from 'vitest';

import { mapOccupancyTrend } from './mappers';

describe('mapOccupancyTrend', () => {
  it('labels use local date/time instead of UTC ISO slices', () => {
    const ts = '2026-08-12T20:00:00+00:00';
    const rows = mapOccupancyTrend([
      { timestamp: ts, current_occupancy: 42 },
    ]);
    expect(rows[0].label).not.toBe('20:00');
    expect(rows[0].label).not.toBe('2026-08-12 20:00');
    const date = new Date(ts);
    const pad = (n: number) => String(n).padStart(2, '0');
    const expectedTime = `${pad(date.getHours())}:${pad(date.getMinutes())}`;
    expect(rows[0].label).toBe(expectedTime);
  });
});
