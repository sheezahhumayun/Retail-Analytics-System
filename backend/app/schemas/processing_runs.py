"""Pydantic schemas for processing run history."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ProcessingRunStatus = Literal["running", "completed", "failed"]


class ProcessingRunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    camera_id: str
    status: ProcessingRunStatus
    started_at: str
    finished_at: str | None = None
    message: str | None = None
    source_path: str


class ProcessingRunDetail(ProcessingRunSummary):
    zones_snapshot: list[dict[str, Any]] = Field(default_factory=list)
    lines_snapshot: list[dict[str, Any]] = Field(default_factory=list)
