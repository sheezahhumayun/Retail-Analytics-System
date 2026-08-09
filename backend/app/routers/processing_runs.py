"""Processing run history and recorded-video playback."""



from __future__ import annotations



from typing import Annotated



from fastapi import APIRouter, Depends

from fastapi.responses import FileResponse

from sqlmodel import select



from database.models import Camera, ProcessingRun



from ..auth import TokenPayload, get_current_user, get_current_user_from_token

from ..deps import DbSession

from ..exceptions import ApiError

from ..schemas.processing_runs import ProcessingRunDetail, ProcessingRunSummary

from ..services.local_media_path import resolve_local_media_path

from ..services.org_scope import require_camera_in_org



router = APIRouter(prefix="/cameras", tags=["Processing runs"])





def _to_summary(run: ProcessingRun) -> ProcessingRunSummary:

    return ProcessingRunSummary(

        id=run.id,

        camera_id=run.camera_id,

        status=run.status,  # type: ignore[arg-type]

        started_at=run.started_at.isoformat(),

        finished_at=run.finished_at.isoformat() if run.finished_at else None,

        message=run.message,

        source_path=run.source_path,

    )





def _to_detail(run: ProcessingRun) -> ProcessingRunDetail:

    summary = _to_summary(run)

    return ProcessingRunDetail(

        **summary.model_dump(),

        zones_snapshot=run.zones_snapshot or [],

        lines_snapshot=run.lines_snapshot or [],

    )





def _get_camera_or_404(session: DbSession, camera_id: str, org_id: str) -> Camera:

    return require_camera_in_org(session, camera_id, org_id)





def _get_run_or_404(session: DbSession, camera_id: str, run_id: str, org_id: str) -> ProcessingRun:

    _get_camera_or_404(session, camera_id, org_id)

    run = session.get(ProcessingRun, run_id)

    if run is None or run.camera_id != camera_id:

        raise ApiError(404, "processing_run_not_found", f"Processing run '{run_id}' not found")

    return run





@router.get(

    "/{camera_id}/processing-runs",

    response_model=list[ProcessingRunSummary],

    summary="List processing runs for a camera",

    description="Return processing run history for a recorded camera, most recent first.",

)

def list_processing_runs(

    camera_id: str,

    session: DbSession,

    user: Annotated[TokenPayload, Depends(get_current_user)],

) -> list[ProcessingRunSummary]:

    camera = _get_camera_or_404(session, camera_id, user.org_id)

    if camera.source_type != "recorded":

        raise ApiError(

            400,

            "invalid_camera_source",

            "Processing runs are only available for recorded-video cameras",

        )

    rows = session.exec(

        select(ProcessingRun)

        .where(ProcessingRun.camera_id == camera_id)

        .order_by(ProcessingRun.started_at.desc())  # type: ignore[attr-defined]

    ).all()

    return [_to_summary(row) for row in rows]





@router.get(

    "/{camera_id}/processing-runs/{run_id}",

    response_model=ProcessingRunDetail,

    summary="Get a processing run",

    description="Return one processing run including geometry snapshots captured at run start.",

)

def get_processing_run(

    camera_id: str,

    run_id: str,

    session: DbSession,

    user: Annotated[TokenPayload, Depends(get_current_user)],

) -> ProcessingRunDetail:

    run = _get_run_or_404(session, camera_id, run_id, user.org_id)

    return _to_detail(run)





@router.get(

    "/{camera_id}/processing-runs/{run_id}/video",

    summary="Playback source video for a processing run",

    description=(

        "Serve the run's snapshotted source file with HTTP Range support for `<video>` "

        "seeking. Authenticate with `Authorization: Bearer` or `?token=<jwt>`."

    ),

    responses={

        200: {"description": "Full video file"},

        206: {"description": "Partial content (Range request)"},

        404: {"description": "Run or source file not found"},

    },

)

def processing_run_video(

    camera_id: str,

    run_id: str,

    session: DbSession,

    user: Annotated[TokenPayload, Depends(get_current_user_from_token)],

) -> FileResponse:

    run = _get_run_or_404(session, camera_id, run_id, user.org_id)

    resolved = resolve_local_media_path(run.source_path)

    if not resolved.is_file():

        raise ApiError(

            404,

            "source_video_unavailable",

            "Source video no longer available at its original path",

        )

    return FileResponse(

        path=str(resolved),

        media_type="video/mp4",

        filename=resolved.name,

    )

