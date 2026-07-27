"""Helpers to inspect zone ENTER/EXIT transitions and detect flapping."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from .types import ZoneEvent, ZoneEventType


@dataclass(frozen=True, slots=True)
class TransitionRecord:
    """One confirmed zone transition for timeline output."""

    frame: int
    timestamp: float
    zone_id: str
    zone_name: str
    track_id: int
    event_type: ZoneEventType


@dataclass(frozen=True, slots=True)
class FlapWarning:
    """ENTER immediately followed by EXIT (or vice versa) within a window."""

    zone_id: str
    track_id: int
    first: TransitionRecord
    second: TransitionRecord
    gap_frames: int


def event_counts(events: list[ZoneEvent]) -> dict[str, int]:
    """Count events by type string."""
    c: Counter[str] = Counter()
    for ev in events:
        c[ev.event_type.value] += 1
    return dict(c)


def extract_transitions(
    events: list[ZoneEvent],
    *,
    frame_timestamps: bool = True,
) -> list[TransitionRecord]:
    """Return only ZONE_ENTER / ZONE_EXIT in chronological order."""
    out: list[TransitionRecord] = []
    for ev in events:
        if ev.event_type not in (ZoneEventType.ZONE_ENTER, ZoneEventType.ZONE_EXIT):
            continue
        frame = int(ev.timestamp) if frame_timestamps else 0
        out.append(
            TransitionRecord(
                frame=frame,
                timestamp=ev.timestamp,
                zone_id=ev.zone_id,
                zone_name=ev.zone_name,
                track_id=ev.track_id,
                event_type=ev.event_type,
            )
        )
    return out


def detect_flapping(
    transitions: list[TransitionRecord],
    *,
    max_gap_frames: int = 3,
) -> list[FlapWarning]:
    """Flag rapid ENTER↔EXIT alternation on the same zone+track."""
    by_key: dict[tuple[str, int], list[TransitionRecord]] = defaultdict(list)
    for tr in transitions:
        by_key[(tr.zone_id, tr.track_id)].append(tr)

    warnings: list[FlapWarning] = []
    for (_zone_id, _track_id), seq in by_key.items():
        for i in range(len(seq) - 1):
            a, b = seq[i], seq[i + 1]
            if a.event_type == b.event_type:
                continue
            gap = b.frame - a.frame
            if gap <= max_gap_frames:
                warnings.append(FlapWarning(a.zone_id, a.track_id, a, b, gap))
    return warnings


def format_transition_timeline(transitions: list[TransitionRecord]) -> str:
    """Human-readable transition log grouped by track."""
    by_track: dict[int, list[TransitionRecord]] = defaultdict(list)
    for tr in transitions:
        by_track[tr.track_id].append(tr)

    lines: list[str] = []
    for track_id in sorted(by_track):
        lines.append(f"track {track_id}:")
        for tr in by_track[track_id]:
            lines.append(
                f"  frame {tr.frame:4d}  {tr.event_type.value:11s}  {tr.zone_name}"
            )
    return "\n".join(lines)
