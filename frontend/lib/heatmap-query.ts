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

/** UTC ISO-8601 instant from a local calendar date + wall-clock time. */
export function localWallClockToUtcIso(date: string, time: string): string {
  return parseLocalDateTime(date, time).toISOString();
}

/**
 * Map a local calendar date range + daily wall-clock window to UTC `from`/`to`
 * ISO datetimes for analytics endpoints (`GET /api/analytics/zones`, traffic, etc.).
 *
 * Uses the same local parsing as {@link localHeatmapRangeToUtcSegments}; unlike
 * heatmap, a single contiguous UTC range is returned (no per-day splitting).
 */
export function localWallClockRangeToUtcIso(
  fromDate: string,
  toDate: string,
  fromTime: string,
  toTime: string,
): { from: string; to: string } {
  const start = parseLocalDateTime(fromDate, fromTime);
  let end = parseLocalDateTime(toDate, toTime);
  if (end.getTime() <= start.getTime()) {
    end = parseLocalDateTime(toDate, '23:59');
  }
  return { from: start.toISOString(), to: end.toISOString() };
}

export type ZonePerformanceDateRange =
  | 'Today'
  | 'Yesterday'
  | 'Last 7 days'
  | 'Last 30 days'
  | 'Custom';

function formatLocalCalendarDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/** Resolve zone-performance pill labels to local calendar start/end dates. */
export function resolveZonePerformanceCalendarDates(
  dateRange: ZonePerformanceDateRange,
  customFrom: string,
  customTo: string,
  now: Date = new Date(),
): { fromDate: string; toDate: string } {
  const todayStr = formatLocalCalendarDate(now);

  switch (dateRange) {
    case 'Today':
      return { fromDate: todayStr, toDate: todayStr };
    case 'Yesterday': {
      const yesterday = new Date(now);
      yesterday.setDate(yesterday.getDate() - 1);
      const yStr = formatLocalCalendarDate(yesterday);
      return { fromDate: yStr, toDate: yStr };
    }
    case 'Last 7 days': {
      const from = new Date(now);
      from.setDate(from.getDate() - 7);
      return { fromDate: formatLocalCalendarDate(from), toDate: todayStr };
    }
    case 'Last 30 days': {
      const from = new Date(now);
      from.setDate(from.getDate() - 30);
      return { fromDate: formatLocalCalendarDate(from), toDate: todayStr };
    }
    case 'Custom':
      return { fromDate: customFrom, toDate: customTo };
    default: {
      const _exhaustive: never = dateRange;
      return _exhaustive;
    }
  }
}
