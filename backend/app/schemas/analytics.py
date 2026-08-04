"""Analytics response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ComparisonStatus = Literal["ok", "module_disabled", "insufficient_history"]


class ComparisonInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: ComparisonStatus
    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    message: str | None = None


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
    comparison: ComparisonInfo | None = None
    prior_buckets: list[TrafficBucket] = Field(default_factory=list)
    prior_total_entries: int | None = None
    prior_total_exits: int | None = None


class OccupancyPoint(BaseModel):
    timestamp: str
    current_occupancy: int


class OccupancyResponse(BaseModel):
    scope: str = Field(description="'camera' or 'store'")
    scope_id: str
    current: int = Field(description="Most recent occupancy value")
    trend: list[OccupancyPoint] = Field(description="Time-series occupancy readings")
    from_: str | None = Field(default=None, alias="from", serialization_alias="from")
    to: str | None = None
    comparison: ComparisonInfo | None = None
    prior_trend: list[OccupancyPoint] = Field(default_factory=list)
    prior_current: int | None = None


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
    comparison: ComparisonInfo | None = None
    prior_buckets: list[ZoneMetricBucket] = Field(default_factory=list)


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
    comparison: ComparisonInfo | None = None
    prior_sessions: list[DwellSession] = Field(default_factory=list)
    prior_count: int | None = None
    prior_avg_dwell_seconds: float | None = None


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
    comparison: ComparisonInfo | None = None
    prior_samples: list[QueueSample] = Field(default_factory=list)
    prior_avg_queue_length: float | None = None
    prior_max_queue_length: int | None = None
