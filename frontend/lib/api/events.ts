import { apiRequest } from "@/lib/api/client";
import type { AnalyticsEvent } from "@/lib/types";

export interface GetEventsParams {
  camera_id?: string;
  event_type?: AnalyticsEvent["event_type"];
  from?: string;
  to?: string;
}

interface BackendEvent {
  id: number;
  camera_id: string;
  zone_id?: string | null;
  track_id?: string | null;
  event_type: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

interface BackendEventListResponse {
  from: string;
  to: string;
  count: number;
  events: BackendEvent[];
}

export async function getEvents(
  params: GetEventsParams = {},
): Promise<AnalyticsEvent[]> {
  const today = new Date().toISOString().slice(0, 10);
  const response = await apiRequest<BackendEventListResponse>("/api/events", {
    query: {
      from: params.from ?? today,
      to: params.to ?? today,
      camera_id: params.camera_id,
      event_type: params.event_type,
    },
  });

  return response.events.map((event) => ({
    event_type: event.event_type as AnalyticsEvent["event_type"],
    camera_id: event.camera_id,
    zone_id: event.zone_id ?? undefined,
    track_id: event.track_id ?? undefined,
    timestamp: event.timestamp,
    metadata: event.metadata ?? {},
  }));
}
