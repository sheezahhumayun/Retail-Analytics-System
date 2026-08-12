import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  formatUtcDate,
  formatUtcTime,
  localHeatmapRangeToUtcSegments,
  parseLocalDateTime,
} from './heatmap-query';

describe('parseLocalDateTime', () => {
  beforeEach(() => {
    vi.stubEnv('TZ', 'Asia/Karachi');
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('interprets date+time in the local timezone', () => {
    const instant = parseLocalDateTime('2026-08-12', '12:46');
    expect(instant.toISOString()).toBe('2026-08-12T07:46:00.000Z');
  });
});

describe('localHeatmapRangeToUtcSegments', () => {
  beforeEach(() => {
    vi.stubEnv('TZ', 'Asia/Karachi');
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('maps default business hours to UTC hours that include noon local', () => {
    const segments = localHeatmapRangeToUtcSegments(
      '2026-08-12',
      '09:00',
      '18:00',
    );
    expect(segments).toEqual([
      { date: '2026-08-12', from_time: '04:00', to_time: '13:00' },
    ]);
  });

  it('includes UTC hour 07 for Pakistan noon processing window', () => {
    const segments = localHeatmapRangeToUtcSegments(
      '2026-08-12',
      '09:00',
      '18:00',
    );
    const [segment] = segments;
    expect(segment.date).toBe('2026-08-12');
    const fromHour = Number(segment.from_time.slice(0, 2));
    const toHour = Number(segment.to_time.slice(0, 2));
    expect(fromHour).toBeLessThanOrEqual(7);
    expect(toHour).toBeGreaterThan(7);
  });

  it('excludes UTC hour 07 when local range is afternoon-only', () => {
    const segments = localHeatmapRangeToUtcSegments(
      '2026-08-12',
      '14:00',
      '18:00',
    );
    expect(segments).toEqual([
      { date: '2026-08-12', from_time: '09:00', to_time: '13:00' },
    ]);
  });

  it('splits across UTC midnight when early-morning local hours cross days', () => {
    const segments = localHeatmapRangeToUtcSegments(
      '2026-08-12',
      '00:00',
      '06:00',
    );
    expect(segments).toEqual([
      { date: '2026-08-11', from_time: '19:00', to_time: '23:59' },
      { date: '2026-08-12', from_time: '00:00', to_time: '01:00' },
    ]);
  });
});

describe('formatUtcDate/formatUtcTime', () => {
  it('formats an instant in UTC', () => {
    const instant = new Date('2026-08-12T07:46:00.000Z');
    expect(formatUtcDate(instant)).toBe('2026-08-12');
    expect(formatUtcTime(instant)).toBe('07:46');
  });
});
