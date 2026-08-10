"""Continuous live-camera analytics worker (detect→track→persist)."""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from sqlmodel import select

from analytics.counting import CountingLine, LineCounter
from analytics.events import AnalyticsEngine, AnalyticsEngineConfig, EventBus
from analytics.modules import (
    MODULE_ENTRY_EXIT,
    MODULE_OCCUPANCY,
    module_enabled,
    normalize_modules,
    zones_for_enabled_modules,
)
from analytics.queues import is_queue_zone
from analytics.zones import Zone, ZoneDetector
from backend.app.services.alert_rules import (
    get_dwell_thresholds,
    get_queue_duration_thresholds,
    get_queue_length_thresholds,
)
from backend.app.services.camera_stream import _is_network_stream, resolve_stream_spec
from backend.app.services.opencv_io import opencv_io
from database.models import Camera, CountingLine as DbCountingLine, Organization, Store, Zone as DbZone
from database.session import session_scope
from database.writer import AnalyticsDbWriter, DbWriterConfig
from inference.detection import create_detector
from inference.tracking import Tracker
from inference.video import create_video_source
from inference.video.base import DEFAULT_LONG_SIDE, DEFAULT_TARGET_FPS
from inference.video.rtsp_timeouts import RTSP_OPEN_READ_TIMEOUT_SEC

from inference.pipeline.process_recorded import _line_from_db, _zone_from_db

if TYPE_CHECKING:
    from inference.detection.base import PersonDetector
    from inference.video.base import VideoSource

logger = logging.getLogger(__name__)

_IDLE_SLEEP_SEC = 0.05

_worker_logger = logging.getLogger("uvicorn.error")
_stop_event = threading.Event()
_coordinator_thread: threading.Thread | None = None
_processing_thread: threading.Thread | None = None
_worker_thread_lock = threading.Lock()

_registry_lock = threading.Lock()
_reconcile_lock = threading.Lock()
_io_workers: dict[str, CameraIoWorker] = {}
_analytics_states: dict[str, CameraAnalyticsState] = {}
_frame_slots: dict[str, FrameSlot] = {}

_shared_writer: AnalyticsDbWriter | None = None
_shared_detector: PersonDetector | None = None


@dataclass
class FrameSlot:
    """Latest frame from an I/O thread (overwrite, no backlog)."""

    lock: threading.Lock = field(default_factory=threading.Lock)
    frame: Any = None
    timestamp: float = 0.0
    frame_id: int = 0


@dataclass
class CameraIoWorker:
    camera_id: str
    thread: threading.Thread
    stop_event: threading.Event
    source: VideoSource


@dataclass
class CameraAnalyticsState:
    camera_id: str
    store_id: str
    org_id: str
    bus: EventBus
    engine: AnalyticsEngine
    tracker: Tracker
    counter: LineCounter | None
    zone_detector: ZoneDetector | None
    pipeline_zones: list[Zone]
    last_processed_frame_id: int = 0


@dataclass(frozen=True)
class CameraPipelineConfig:
    camera_id: str
    store_id: str
    org_id: str
    rtsp_url: str
    enabled_modules: frozenset[str]
    pipeline_zones: list[Zone]
    counting_line: CountingLine | None
    needs_counting: bool
    needs_zone_detector: bool
    dwell_thresholds: dict[str, float | None] | None
    queue_length_thresholds: dict[str, int | None] | None
    queue_duration_thresholds: dict[str, float | None] | None


def _create_io_source(rtsp_url: str, camera_id: str) -> VideoSource:
    resolved = resolve_stream_spec(rtsp_url)
    common: dict[str, Any] = {
        "target_fps": DEFAULT_TARGET_FPS,
        "target_long_side": DEFAULT_LONG_SIDE,
    }
    if _is_network_stream(resolved):
        return create_video_source(
            resolved,
            camera_id=camera_id,
            timeout_sec=RTSP_OPEN_READ_TIMEOUT_SEC,
            **common,
        )
    return create_video_source(resolved, loop=True, **common)


def _load_pipeline_config(session, camera: Camera) -> CameraPipelineConfig | None:
    if not camera.rtsp_url:
        return None
    store = session.get(Store, camera.store_id)
    if store is None:
        return None
    org = session.get(Organization, store.org_id)
    if org is None or org.status != "active":
        return None

    enabled = frozenset(normalize_modules(camera.analytics_modules))
    db_zones = list(
        session.exec(
            select(DbZone).where(
                DbZone.camera_id == camera.id,
                DbZone.status != "disabled",
            )
        ).all()
    )
    all_zones = [_zone_from_db(z) for z in db_zones if z.analytics_enabled]
    pipeline_zones = zones_for_enabled_modules(all_zones, enabled)

    db_line = session.exec(
        select(DbCountingLine).where(
            DbCountingLine.camera_id == camera.id,
            DbCountingLine.status != "disabled",
        )
    ).first()
    counting_line = _line_from_db(db_line) if db_line is not None else None

    needs_counting = (
        module_enabled(enabled, MODULE_ENTRY_EXIT)
        or module_enabled(enabled, MODULE_OCCUPANCY)
    )
    needs_zone_detector = bool(pipeline_zones)

    dwell_zones = [z.zone_id for z in pipeline_zones if not is_queue_zone(z)]
    queue_zones = [z.zone_id for z in pipeline_zones if is_queue_zone(z)]

    dwell_thresholds = (
        get_dwell_thresholds(dwell_zones, camera.store_id, session=session)
        if dwell_zones
        else None
    )
    queue_length_thresholds = (
        get_queue_length_thresholds(queue_zones, camera.store_id, session=session)
        if queue_zones
        else None
    )
    queue_duration_thresholds = (
        get_queue_duration_thresholds(queue_zones, camera.store_id, session=session)
        if queue_zones
        else None
    )

    return CameraPipelineConfig(
        camera_id=camera.id,
        store_id=camera.store_id,
        org_id=store.org_id,
        rtsp_url=camera.rtsp_url,
        enabled_modules=enabled,
        pipeline_zones=pipeline_zones,
        counting_line=counting_line,
        needs_counting=needs_counting,
        needs_zone_detector=needs_zone_detector,
        dwell_thresholds=dwell_thresholds,
        queue_length_thresholds=queue_length_thresholds,
        queue_duration_thresholds=queue_duration_thresholds,
    )


def _eligible_live_cameras(session) -> list[Camera]:
    return list(
        session.exec(
            select(Camera)
            .join(Store, Camera.store_id == Store.id)
            .join(Organization, Store.org_id == Organization.id)
            .where(
                Camera.source_type == "live",
                Camera.status != "disabled",
                Camera.status != "processing",
                Organization.status == "active",
                Camera.rtsp_url.isnot(None),  # type: ignore[union-attr]
            )
        ).all()
    )


def _build_analytics_state(
    config: CameraPipelineConfig,
    writer: AnalyticsDbWriter,
) -> CameraAnalyticsState:
    bus = EventBus()
    writer.subscribe(bus)

    engine = AnalyticsEngine(
        bus,
        AnalyticsEngineConfig(
            camera_ids=[config.camera_id],
            zones=config.pipeline_zones,
            store_id=config.store_id,
            db_writer=writer,
            enabled_modules=config.enabled_modules,
            dwell_thresholds=config.dwell_thresholds,
            queue_length_thresholds=config.queue_length_thresholds,
            queue_duration_thresholds=config.queue_duration_thresholds,
        ),
    )

    counter = None
    if config.counting_line is not None and config.needs_counting:
        counter = LineCounter(config.counting_line, event_bus=bus)

    zone_detector = (
        ZoneDetector(config.pipeline_zones) if config.needs_zone_detector else None
    )

    return CameraAnalyticsState(
        camera_id=config.camera_id,
        store_id=config.store_id,
        org_id=config.org_id,
        bus=bus,
        engine=engine,
        tracker=Tracker(camera_id=config.camera_id, min_confirmation_frames=2),
        counter=counter,
        zone_detector=zone_detector,
        pipeline_zones=config.pipeline_zones,
    )


def _io_thread_main(
    camera_id: str,
    source: VideoSource,
    slot: FrameSlot,
    stop_event: threading.Event,
) -> None:
    try:
        with opencv_io():
            source.open()
        while not stop_event.is_set():
            with opencv_io():
                ok, frame = source.read()
            if ok and frame is not None:
                with slot.lock:
                    slot.frame = frame.copy()
                    slot.timestamp = source.get_last_timestamp()
                    slot.frame_id += 1
            elif not source.is_live():
                break
    except Exception:
        logger.exception("Live analytics I/O failed for camera %s", camera_id)
    finally:
        try:
            with opencv_io():
                source.release()
            _worker_logger.info(
                "Released video source for camera %s (opened=%s)",
                camera_id,
                getattr(source, "_opened", "unknown"),
            )
        except Exception:
            logger.exception("Failed to release source for camera %s", camera_id)


def _start_camera(config: CameraPipelineConfig, writer: AnalyticsDbWriter) -> None:
    with _registry_lock:
        if config.camera_id in _analytics_states:
            return

    slot = FrameSlot()
    source = _create_io_source(config.rtsp_url, config.camera_id)
    stop_event = threading.Event()
    thread = threading.Thread(
        target=_io_thread_main,
        args=(config.camera_id, source, slot, stop_event),
        name=f"live-io-{config.camera_id}",
        daemon=True,
    )

    writer.add_camera(
        config.camera_id,
        config.store_id,
        config.enabled_modules,
        zones=config.pipeline_zones,
    )
    state = _build_analytics_state(config, writer)

    with _registry_lock:
        _frame_slots[config.camera_id] = slot
        _io_workers[config.camera_id] = CameraIoWorker(
            camera_id=config.camera_id,
            thread=thread,
            stop_event=stop_event,
            source=source,
        )
        _analytics_states[config.camera_id] = state

    thread.start()
    _worker_logger.info("Live analytics started for camera %s", config.camera_id)


def _stop_camera(camera_id: str) -> None:
    with _registry_lock:
        io_worker = _io_workers.pop(camera_id, None)
        state = _analytics_states.pop(camera_id, None)
        _frame_slots.pop(camera_id, None)

    if io_worker is not None:
        io_worker.stop_event.set()
        io_worker.thread.join(timeout=5)
        _worker_logger.info(
            "I/O thread join for camera %s: alive=%s name=%s",
            camera_id,
            io_worker.thread.is_alive(),
            io_worker.thread.name,
        )

    writer = _shared_writer
    if writer is not None and state is not None:
        writer.unsubscribe(state.bus)

    if writer is not None:
        writer.remove_camera(camera_id)

    if state is not None or io_worker is not None:
        _worker_logger.info("Live analytics stopped for camera %s", camera_id)


def _process_camera_frame(
    camera_id: str,
    state: CameraAnalyticsState,
    slot: FrameSlot,
    detector: PersonDetector,
) -> bool:
    with slot.lock:
        if slot.frame is None or slot.frame_id <= state.last_processed_frame_id:
            return False
        frame = slot.frame
        ts = slot.timestamp
        frame_id = slot.frame_id

    dets = detector.detect(frame, camera_id=camera_id, timestamp=ts)
    tracks = state.tracker.update(dets)
    if state.counter is not None:
        state.counter.update(tracks)
    if state.zone_detector is not None:
        for zone_event in state.zone_detector.update(tracks):
            state.engine.process_zone_event(zone_event)
    state.engine.close_stale_dwell_sessions(ts)
    state.last_processed_frame_id = frame_id
    return True


def _processing_loop() -> None:
    while not _stop_event.is_set():
        detector = _shared_detector
        if detector is None:
            time.sleep(_IDLE_SLEEP_SEC)
            continue

        with _registry_lock:
            camera_ids = list(_analytics_states.keys())

        processed_any = False
        for camera_id in camera_ids:
            with _registry_lock:
                state = _analytics_states.get(camera_id)
                slot = _frame_slots.get(camera_id)
            if state is None or slot is None:
                continue
            try:
                if _process_camera_frame(camera_id, state, slot, detector):
                    processed_any = True
            except Exception:
                logger.exception("Live analytics processing failed for camera %s", camera_id)

        if not processed_any:
            time.sleep(_IDLE_SLEEP_SEC)


def reconcile_live_cameras() -> tuple[int, int]:
    """Start/stop cameras to match DB eligibility. Returns (started, stopped) counts."""
    writer = _shared_writer
    if writer is None:
        return 0, 0

    with _reconcile_lock:
        with session_scope() as session:
            eligible = _eligible_live_cameras(session)
            configs: dict[str, CameraPipelineConfig] = {}
            for camera in eligible:
                config = _load_pipeline_config(session, camera)
                if config is not None:
                    configs[camera.id] = config

        with _registry_lock:
            running = set(_analytics_states.keys())

        eligible_ids = set(configs.keys())
        to_start = eligible_ids - running
        to_stop = running - eligible_ids

        for camera_id in to_stop:
            _stop_camera(camera_id)

        for camera_id in to_start:
            _start_camera(configs[camera_id], writer)

        return len(to_start), len(to_stop)


def stop_live_workers_for_org(org_id: str) -> int:
    """Immediately stop live analytics for all cameras in ``org_id``."""
    with _registry_lock:
        targets = [
            camera_id
            for camera_id, state in _analytics_states.items()
            if state.org_id == org_id
        ]

    for camera_id in targets:
        _stop_camera(camera_id)

    if targets:
        _worker_logger.info(
            "Stopped live analytics for %d camera(s) in org %s",
            len(targets),
            org_id,
        )
    return len(targets)


def _coordinator_loop(reconcile_interval_seconds: int) -> None:
    while not _stop_event.is_set():
        try:
            started, stopped = reconcile_live_cameras()
            if started or stopped:
                _worker_logger.info(
                    "Live analytics reconcile: started %d, stopped %d camera(s)",
                    started,
                    stopped,
                )
        except Exception:
            logger.exception("Live analytics reconcile failed")
        if _stop_event.wait(timeout=reconcile_interval_seconds):
            break


def _start_live_analytics_worker(reconcile_interval_seconds: int) -> None:
    global _coordinator_thread, _processing_thread, _shared_writer, _shared_detector

    with _worker_thread_lock:
        if reconcile_interval_seconds <= 0 or _coordinator_thread is not None:
            return

        _stop_event.clear()
        _shared_writer = AnalyticsDbWriter(
            DbWriterConfig(
                store_id="",
                camera_store_map={},
                zones=[],
                camera_modules={},
            )
        )
        _shared_detector = create_detector()
        _shared_detector.__enter__()

        _processing_thread = threading.Thread(
            target=_processing_loop,
            name="live-analytics-processing",
            daemon=True,
        )
        _processing_thread.start()

        _coordinator_thread = threading.Thread(
            target=_coordinator_loop,
            args=(reconcile_interval_seconds,),
            name="live-analytics-coordinator",
            daemon=True,
        )
        _coordinator_thread.start()

        _worker_logger.info(
            "Live analytics worker started (reconcile_interval=%ds)",
            reconcile_interval_seconds,
        )


def _stop_live_analytics_worker() -> None:
    global _coordinator_thread, _processing_thread, _shared_writer, _shared_detector

    _stop_event.set()

    with _registry_lock:
        camera_ids = list(_analytics_states.keys())
    for camera_id in camera_ids:
        _stop_camera(camera_id)

    with _worker_thread_lock:
        for thread in (_coordinator_thread, _processing_thread):
            if thread is not None and thread.is_alive():
                thread.join(timeout=5)
        _coordinator_thread = None
        _processing_thread = None

    if _shared_detector is not None:
        try:
            _shared_detector.__exit__(None, None, None)
        except Exception:
            logger.exception("Failed to release shared detector")
        _shared_detector = None

    if _shared_writer is not None:
        _shared_writer.close()
        _shared_writer = None

    _worker_logger.info("Live analytics worker stopped")


def get_running_live_camera_ids() -> list[str]:
    """Return camera ids currently managed by the live analytics worker (tests/diagnostics)."""
    with _registry_lock:
        return list(_analytics_states.keys())


def get_io_worker_diagnostics() -> dict[str, dict[str, object]]:
    """Per-camera I/O thread and source state for verification/diagnostics."""
    with _registry_lock:
        out: dict[str, dict[str, object]] = {}
        for camera_id, worker in _io_workers.items():
            source = worker.source
            out[camera_id] = {
                "thread_name": worker.thread.name,
                "thread_alive": worker.thread.is_alive(),
                "source_opened": getattr(source, "_opened", None),
                "source_state": (
                    source.get_state().value if hasattr(source, "get_state") else None
                ),
            }
        return out


def list_live_io_thread_names() -> list[str]:
    """Return names of registered live I/O threads (alive or dead until joined)."""
    with _registry_lock:
        return [worker.thread.name for worker in _io_workers.values()]
