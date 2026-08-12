"""Query recent processing runs and camera last_processed_at."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlmodel import select

from database.models import Camera, ProcessingRun
from database.session import session_scope


def main() -> None:
    with session_scope() as s:
        runs = list(
            s.exec(
                select(ProcessingRun).order_by(ProcessingRun.started_at.desc()).limit(5)
            ).all()
        )
        print("=== Recent ProcessingRuns ===")
        for r in runs:
            print(f"run_id={r.id[:16]} camera={r.camera_id} status={r.status}")
            print(f"  started_at={r.started_at!r}")
            print(f"  finished_at={r.finished_at!r}")
            if r.started_at:
                print(f"  started_at.isoformat()={r.started_at.isoformat()}")

        print()
        cams = list(
            s.exec(
                select(Camera)
                .where(Camera.last_processed_at.isnot(None))
                .order_by(Camera.last_processed_at.desc())
                .limit(5)
            ).all()
        )
        print("=== Cameras last_processed_at ===")
        for c in cams:
            print(f"camera={c.id}")
            print(f"  last_processed_at={c.last_processed_at!r}")
            if c.last_processed_at:
                print(f"  isoformat()={c.last_processed_at.isoformat()}")


if __name__ == "__main__":
    main()
