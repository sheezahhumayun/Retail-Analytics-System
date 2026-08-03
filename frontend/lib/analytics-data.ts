import type { DateRangeKey } from "@/lib/types";

/** UI label for analytics chart axis intervals — not business data. */
export function getIntervalLabel(range: DateRangeKey): string {
  switch (range) {
    case "hour":
      return "5-min window";
    case "day":
      return "Hour";
    case "week":
    case "month":
      return "Day";
    case "custom":
      return "Custom range";
    default: {
      const _exhaustive: never = range;
      return _exhaustive;
    }
  }
}
