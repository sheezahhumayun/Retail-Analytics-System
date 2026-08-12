'use client';

import { useEffect, useState } from 'react';
import { X } from 'lucide-react';

import { ProcessingRunPlayer } from '@/components/cameras/processing-run-player';
import {
  LIVE_CAMERA_OVERLAYS,
  OverlayToggles,
} from '@/components/cameras/overlay-toggles';
import { mapProcessingRunSnapshotsToOverlays } from '@/lib/api/mappers';
import {
  getProcessingRun,
  getProcessingRunVideoUrl,
  getProcessingRuns,
  type ProcessingRunSummary,
} from '@/lib/api/processing-runs';
import type { OverlayState } from '@/lib/types';
import { formatUtcDateTime } from '@/lib/format-datetime';

export function ProcessingRunPreviewModal({
  cameraId,
  cameraName,
  isOpen,
  onClose,
}: {
  cameraId: string;
  cameraName: string;
  isOpen: boolean;
  onClose: () => void;
}) {
  const [runs, setRuns] = useState<ProcessingRunSummary[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [overlays, setOverlays] = useState<OverlayState>(LIVE_CAMERA_OVERLAYS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [zones, setZones] = useState<ReturnType<typeof mapProcessingRunSnapshotsToOverlays>['zones']>([]);
  const [countingLines, setCountingLines] = useState<
    ReturnType<typeof mapProcessingRunSnapshotsToOverlays>['countingLines']
  >([]);

  useEffect(() => {
    if (!isOpen) return;

    let cancelled = false;
    setLoading(true);
    setError('');

    async function loadRuns() {
      try {
        const allRuns = await getProcessingRuns(cameraId);
        const completed = allRuns.filter((run) => run.status === 'completed');
        if (cancelled) return;
        setRuns(completed);
        setSelectedRunId(completed[0]?.id ?? null);
        if (completed.length === 0) {
          setError('No completed processing runs are available for this camera yet.');
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load processing runs');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadRuns();
    return () => {
      cancelled = true;
    };
  }, [cameraId, isOpen]);

  useEffect(() => {
    if (!isOpen || selectedRunId === null) return;
    const runId = selectedRunId;

    let cancelled = false;

    async function loadRunDetail() {
      try {
        const detail = await getProcessingRun(cameraId, runId);
        if (cancelled) return;
        const mapped = mapProcessingRunSnapshotsToOverlays(
          detail.zones_snapshot,
          detail.lines_snapshot,
        );
        setZones(mapped.zones);
        setCountingLines(mapped.countingLines);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load run detail');
        }
      }
    }

    loadRunDetail();
    return () => {
      cancelled = true;
    };
  }, [cameraId, isOpen, selectedRunId]);

  if (!isOpen) return null;

  const videoUrl = selectedRunId ? getProcessingRunVideoUrl(cameraId, selectedRunId) : null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-label={`Preview last processed run for ${cameraName}`}
    >
      <div
        className="absolute inset-0 bg-background/80 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      <div className="relative z-10 flex max-h-[90dvh] w-full max-w-4xl flex-col overflow-hidden rounded-xl border border-border bg-card shadow-lg">
        <div className="flex items-center justify-between gap-4 border-b border-border px-5 py-3.5">
          <div>
            <h2 className="text-base font-semibold text-foreground">Preview last processed</h2>
            <p className="text-sm text-muted-foreground">{cameraName}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {loading && <p className="text-sm text-muted-foreground">Loading processing runs…</p>}
          {error && <p className="text-sm text-destructive">{error}</p>}

          {!loading && runs.length > 1 && (
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Run</label>
              <select
                value={selectedRunId ?? ''}
                onChange={(e) => setSelectedRunId(e.target.value)}
                className="w-full px-3 py-2 bg-muted border border-border rounded text-foreground"
              >
                {runs.map((run) => (
                  <option key={run.id} value={run.id}>
                    {formatUtcDateTime(run.started_at)}
                    {run.finished_at ? ` — ${formatUtcDateTime(run.finished_at)}` : ''}
                  </option>
                ))}
              </select>
            </div>
          )}

          {videoUrl && selectedRunId && !error && (
            <>
              <OverlayToggles value={overlays} onChange={setOverlays} mode="live" size="md" />
              <ProcessingRunPlayer
                videoUrl={videoUrl}
                zones={zones}
                countingLines={countingLines}
                overlays={overlays}
                playerId={selectedRunId}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
