import { describe, expect, it } from 'vitest';

import {
  formatUtcDateTime,
  formatUtcLocalDateYMD,
  formatUtcLocalTimeHHMM,
  parseUtcDateTime,
} from './format-datetime';

describe('parseUtcDateTime', () => {
  it('treats naive ISO strings as UTC', () => {
    const date = parseUtcDateTime('2026-08-12T07:20:45.688010');
    expect(date.toISOString()).toBe('2026-08-12T07:20:45.688Z');
  });

  it('preserves explicit UTC offset suffixes', () => {
    const date = parseUtcDateTime('2026-08-12T07:22:16.985200+00:00');
    expect(date.toISOString()).toBe('2026-08-12T07:22:16.985Z');
  });

  it('preserves Z suffix', () => {
    const date = parseUtcDateTime('2026-08-12T07:22:16.985Z');
    expect(date.toISOString()).toBe('2026-08-12T07:22:16.985Z');
  });
});

describe('formatUtcDateTime', () => {
  it('formats naive UTC as local wall time in Asia/Karachi', () => {
    const formatted = formatUtcDateTime('2026-08-12T07:20:45.688010', {
      timeZone: 'Asia/Karachi',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
    expect(formatted).toContain('12:20');
  });

  it('matches offset-aware timestamps', () => {
    const naive = formatUtcDateTime('2026-08-12T07:22:16.985200', {
      timeZone: 'Asia/Karachi',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
    const aware = formatUtcDateTime('2026-08-12T07:22:16.985200+00:00', {
      timeZone: 'Asia/Karachi',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
    expect(naive).toBe(aware);
  });
});

describe('formatUtcLocalDateYMD / formatUtcLocalTimeHHMM', () => {
  const utcNearBoundary = '2026-08-12T20:00:00+00:00';

  it('derives local date and time from parsed UTC instant', () => {
    const date = parseUtcDateTime(utcNearBoundary);
    expect(formatUtcLocalDateYMD(utcNearBoundary)).toBe(
      `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`,
    );
    expect(formatUtcLocalTimeHHMM(utcNearBoundary)).toBe(
      `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`,
    );
  });

  it('matches offset-aware and naive UTC strings', () => {
    const aware = '2026-08-12T20:00:00+00:00';
    const naive = '2026-08-12T20:00:00';
    expect(formatUtcLocalTimeHHMM(naive)).toBe(formatUtcLocalTimeHHMM(aware));
    expect(formatUtcLocalDateYMD(naive)).toBe(formatUtcLocalDateYMD(aware));
  });
});
