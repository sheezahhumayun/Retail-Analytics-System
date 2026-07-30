"""Analytics response schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TrafficBucket(BaseModel):
    metric_date: str = Field(description="YYYY-MM-DD")
    hour: int = Field(ge=0, le=23)
    entries: int
    exits: int


class TrafficResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    store_id: str
    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    buckets: list[TrafficBucket]
    total_entries: int
    total_exits: int


class OccupancyPoint(BaseModel):
    timestamp: str
    current_occupancy: int


class OccupancyResponse(BaseModel):
    scope: str = Field(description="'camera' or 'store'")
    scope_id: str
    current: int = Field(description="Most recent occupancy value")
    trend: list[OccupancyPoint] = Field(description="Time-series occupancy readings")


class ZoneMetricBucket(BaseModel):
    metric_date: str
    hour: int
    visitors: int
    avg_dwell: float
    max_dwell: float
    min_dwell: float | None
    dwell_count: int


class ZoneAnalyticsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    zone_id: str
    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    buckets: list[ZoneMetricBucket]


class DwellSession(BaseModel):
    id: int
    zone_id: str
    track_id: str
    enter_ts: str
    exit_ts: str
    dwell_seconds: float


class DwellResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    zone_id: str
    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    sessions: list[DwellSession]
    count: int
    avg_dwell_seconds: float | None


class HeatmapSpec(BaseModel):
    width: int
    height: int
    grid_scale: int


class HeatmapResponse(BaseModel):
    camera_id: str
    date: str
    from_time: str
    to_time: str
    spec: HeatmapSpec
    density: list[list[float]]
    trajectory: list[list[float]]
    total_hits: float


class QueueSample(BaseModel):
    timestamp: str
    queue_length: int
    estimated_wait: float


class QueueAnalyticsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    zone_id: str
    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    samples: list[QueueSample]
    avg_queue_length: float | None
    max_queue_length: int | None
