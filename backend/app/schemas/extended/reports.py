"""Report payload schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ReportType = Literal["traffic", "occupancy", "zones", "dwell", "queues"]


class ReportHeader(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    store_id: str
    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    generated_at: str
    report_type: ReportType


class ReportKpi(BaseModel):
    key: str
    label: str
    value: int | float


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
