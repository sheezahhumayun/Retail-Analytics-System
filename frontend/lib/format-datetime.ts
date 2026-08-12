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
