"""Admin alert_rules schemas (Module 15, Phase 4)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AlertRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_type: str
    store_id: str | None = None
    zone_id: str | None = None
    threshold: float
    severity: str
    enabled: bool
    created_at: str
    updated_at: str


class AlertRuleUpdate(BaseModel):
    threshold: float = Field(gt=0, description="Threshold must be greater than zero")
    severity: Literal["info", "warning", "critical"]
    enabled: bool
