"""FastAPI dependencies."""

from __future__ import annotations

from collections.abc import Generator
from datetime import date, datetime, time
from typing import Annotated

from fastapi import Depends, Query
from sqlmodel import Session

from database.session import get_engine
from sqlmodel import Session as SQLSession

from .exceptions import ApiError


def get_db() -> Generator[Session, None, None]:
    session = SQLSession(get_engine())
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


DbSession = Annotated[Session, Depends(get_db)]


def parse_datetime(value: str, *, param: str) -> datetime:
    """Parse ISO-8601 datetime strings with clear errors."""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ApiError(
            400,
            "invalid_datetime",
            f"Invalid datetime for '{param}': expected ISO-8601 format",
            details={"param": param, "value": value},
        ) from exc
    if dt.tzinfo is None:
        from datetime import timezone

        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def parse_date(value: str, *, param: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ApiError(
            400,
            "invalid_date",
            f"Invalid date for '{param}': expected YYYY-MM-DD",
            details={"param": param, "value": value},
        ) from exc


def parse_time(value: str, *, param: str) -> time:
    try:
        parts = value.split(":")
        if len(parts) == 2:
            return time(int(parts[0]), int(parts[1]))
        if len(parts) == 3:
            return time(int(parts[0]), int(parts[1]), int(parts[2]))
        raise ValueError("bad format")
    except (ValueError, IndexError) as exc:
        raise ApiError(
            400,
            "invalid_time",
            f"Invalid time for '{param}': expected HH:MM or HH:MM:SS",
            details={"param": param, "value": value},
        ) from exc


def require_date_range(
    from_: Annotated[str, Query(alias="from", description="Start of range (ISO date or datetime)")],
    to: Annotated[str, Query(description="End of range (ISO date or datetime)")],
) -> tuple[datetime, datetime]:
    """Parse from/to — accepts date-only (start/end of day) or full datetimes."""
    start = _parse_range_bound(from_, param="from", is_end=False)
    end = _parse_range_bound(to, param="to", is_end=True)
    if start > end:
        raise ApiError(
            400,
            "invalid_date_range",
            "'from' must be before or equal to 'to'",
            details={"from": from_, "to": to},
        )
    return start, end


def _parse_range_bound(value: str, *, param: str, is_end: bool) -> datetime:
    from datetime import timezone

    if "T" in value or " " in value or "+" in value or value.endswith("Z"):
        return parse_datetime(value, param=param)
    d = parse_date(value, param=param)
    if is_end:
        return datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=timezone.utc)
    return datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=timezone.utc)
