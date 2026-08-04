"""Report payload schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ..analytics import ComparisonInfo

ReportType = Literal["traffic", "occupancy", "zones", "dwell", "queues"]


class ReportCoverage(BaseModel):
    module: str
    cameras_in_scope: int
    cameras_eligible: int
    zones_in_scope: int
    zones_eligible: int


class ReportExclusion(BaseModel):
    kind: Literal["camera", "zone"]
    id: str
    name: str
    module: str
    reason: str


class ReportHeader(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    store_id: str
    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    generated_at: str
    report_type: ReportType
    camera_id: str | None = None
    coverage: ReportCoverage | None = None


class ReportKpi(BaseModel):
    key: str
    label: str
    value: int | float | str


class ReportSeries(BaseModel):
    name: str
    points: list[dict[str, Any]]


class ReportRow(BaseModel):
    columns: dict[str, Any]


class ReportPayload(BaseModel):
    header: ReportHeader
    kpis: list[ReportKpi]
    series: list[ReportSeries]
    table: list[ReportRow]
    exclusions: list[ReportExclusion] = Field(default_factory=list)
    footnotes: list[str] = Field(default_factory=list)
    comparison: ComparisonInfo | None = None
