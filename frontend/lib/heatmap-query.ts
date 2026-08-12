/**
 * Convert browser-local heatmap time-range selections into UTC API query segments.
 *
 * Heatmap buckets are stored by real UTC hour. The API accepts one calendar `date`
 * plus `from_time` / `to_time` per request (interpreted as UTC when store_timezone
 * is UTC). A local range that crosses a UTC midnight is split into multiple segments.
 */

export interface UtcHeatmapQuerySegment {
  /** UTC calendar date (YYYY-MM-DD). */
  date: string;
  /** UTC time of day (HH:MM). */
  from_time: string;
  /** UTC time of day (HH:MM). */
  to_time: string;
}

/** Combine a local calendar date and wall-clock time into a Date (browser timezone). */
export function parseLocalDateTime(date: string, time: string): Date {
  const normalized = time.length === 5 ? `${time}:00` : time;
  return new Date(`${date}T${normalized}`);
}

/** UTC calendar date YYYY-MM-DD from an instant. */
export function formatUtcDate(instant: Date): string {
  return instant.toISOString().slice(0, 10);
}

/** UTC time HH:MM from an instant. */
export function formatUtcTime(instant: Date): string {
  return instant.toISOString().slice(11, 16);
}

function utcMidnightAfter(instant: Date): Date {
  return new Date(
    Date.UTC(
      instant.getUTCFullYear(),
      instant.getUTCMonth(),
      instant.getUTCDate() + 1,
    ),
  );
}

/**
 * Map a local date + time range to one or more UTC API query segments.
 *
 * `fromTime` / `toTime` are the user's wall-clock values (same timezone as `date`).
 * When the range crosses UTC midnight, multiple segments are returned so each
 * request stays within a single UTC calendar date.
 */
export function localHeatmapRangeToUtcSegments(
  date: string,
  fromTime: string,
  toTime: string,
): UtcHeatmapQuerySegment[] {
  const start = parseLocalDateTime(date, fromTime);
  let end = parseLocalDateTime(date, toTime);
  if (end.getTime() <= start.getTime()) {
    end = parseLocalDateTime(date, '23:59');
  }

  const segments: UtcHeatmapQuerySegment[] = [];
  let cursor = start;

  while (cursor.getTime() < end.getTime()) {
    const segmentDate = formatUtcDate(cursor);
    const segmentFrom = formatUtcTime(cursor);
    const dayEnd = utcMidnightAfter(cursor);
    const sliceEnd = end.getTime() < dayEnd.getTime() ? end : dayEnd;

    if (sliceEnd.getTime() > cursor.getTime()) {
      const segmentTo =
        sliceEnd.getTime() === dayEnd.getTime()
          ? '23:59'
          : formatUtcTime(sliceEnd);
      segments.push({
        date: segmentDate,
        from_time: segmentFrom,
        to_time: segmentTo,
      });
    }

    cursor = sliceEnd;
  }

  return segments;
}
