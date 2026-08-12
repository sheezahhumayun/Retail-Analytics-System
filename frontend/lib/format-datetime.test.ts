import { describe, expect, it } from 'vitest';

import { formatUtcDateTime, parseUtcDateTime } from './format-datetime';

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
