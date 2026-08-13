/** True when an ISO-8601 string already carries an explicit UTC/offset suffix. */
const HAS_TIMEZONE_SUFFIX = /(?:Z|[+-]\d{2}:\d{2})$/;

/**
 * Parse a backend timestamp for display.
 *
 * API values are UTC internally. Some fields (e.g. processing_run.started_at)
 * are serialized without a timezone suffix; JavaScript would otherwise treat
 * those as local wall time. Naive strings are interpreted as UTC.
 */
export function parseUtcDateTime(value: string): Date {
  const trimmed = value.trim();
  if (!trimmed) return new Date(Number.NaN);
  if (HAS_TIMEZONE_SUFFIX.test(trimmed)) {
    return new Date(trimmed);
  }
  return new Date(`${trimmed}Z`);
}

/** Format a UTC backend timestamp in the browser's local timezone. */
export function formatUtcDateTime(
  value: string,
  options?: Intl.DateTimeFormatOptions,
): string {
  const date = parseUtcDateTime(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    ...options,
  });
}

/** Local calendar date YYYY-MM-DD from a UTC backend timestamp. */
export function formatUtcLocalDateYMD(value: string): string {
  const date = parseUtcDateTime(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/** Local time of day HH:MM (24h) from a UTC backend timestamp. */
export function formatUtcLocalTimeHHMM(value: string): string {
  const date = parseUtcDateTime(value);
  if (Number.isNaN(date.getTime())) {
    return '00:00';
  }
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
}
