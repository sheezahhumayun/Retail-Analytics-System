'use client';

import { useEffect, useMemo, useState } from 'react';
import { Calendar, Clock, Loader, X } from 'lucide-react';
import type { AdminCamera } from '@/lib/types';
import {
  getCameraProcessStatus,
  processCameraVideo,
  testCamera,
} from '@/lib/api/cameras';

interface ProcessVideoModalProps {
  camera: AdminCamera;
  isOpen: boolean;
  onClose: () => void;
  onComplete?: (camera: AdminCamera) => void;
}

function formatLocalDateTime(date: Date): { date: string; time: string } {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return { date: `${year}-${month}-${day}`, time: `${hours}:${minutes}` };
}

function combineLocalDateTime(date: string, time: string): Date | null {
  if (!date || !time) return null;
  const parsed = new Date(`${date}T${time}`);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function ProcessVideoModal({
  camera,
  isOpen,
  onClose,
  onComplete,
}: ProcessVideoModalProps) {
  const [loadingDuration, setLoadingDuration] = useState(true);
  const [durationSeconds, setDurationSeconds] = useState<number | null>(null);
  const [durationError, setDurationError] = useState('');
  const [startDate, setStartDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [processing, setProcessing] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isOpen) return;

    let cancelled = false;
    const defaults = formatLocalDateTime(new Date());
    setStartDate(defaults.date);
    setStartTime(defaults.time);
    setLoadingDuration(true);
    setDurationSeconds(null);
    setDurationError('');
    setProcessing(false);
    setStatusMessage('');
    setError('');

    async function loadDuration() {
      try {
        const result = await testCamera(camera.id);
        if (cancelled) return;
        if (result.status === 'error') {
          setDurationError(result.error);
          return;
        }
        const duration =
          'duration_seconds' in result && typeof result.duration_seconds === 'number'
            ? result.duration_seconds
            : null;
        if (duration === null || duration <= 0) {
          setDurationError('Could not determine video duration. You can still process without a start time.');
          return;
        }
        setDurationSeconds(duration);
      } catch (err) {
        if (cancelled) return;
        setDurationError(
          err instanceof Error ? err.message : 'Failed to load video duration',
        );
      } finally {
        if (!cancelled) setLoadingDuration(false);
      }
    }

    loadDuration();
    return () => {
      cancelled = true;
    };
  }, [camera.id, isOpen]);

  const startDateTime = useMemo(
    () => combineLocalDateTime(startDate, startTime),
    [startDate, startTime],
  );

  const endDateTime = useMemo(() => {
    if (!startDateTime || durationSeconds === null) return null;
    return new Date(startDateTime.getTime() + durationSeconds * 1000);
  }, [startDateTime, durationSeconds]);

  const endFields = endDateTime ? formatLocalDateTime(endDateTime) : null;

  const handleSubmit = async () => {
    setError('');
    setStatusMessage('');
    setProcessing(true);
    try {
      const recordingStart =
        startDateTime !== null ? startDateTime.toISOString() : undefined;
      let status = await processCameraVideo(camera.id, {
        recording_start: recordingStart,
      });
      while (status.status === 'running') {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        status = await getCameraProcessStatus(camera.id);
        setStatusMessage(status.message ?? 'Processing video…');
      }
      if (status.status === 'failed') {
        setError(status.message ?? 'Video processing failed');
        return;
      }
      onComplete?.({
        ...camera,
        lastProcessedAt: status.finished_at ?? new Date().toISOString(),
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process video');
    } finally {
      setProcessing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-lg bg-card border border-border rounded-lg shadow-lg">
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">Process Recorded Video</h2>
          <button
            type="button"
            onClick={onClose}
            disabled={processing}
            className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <p className="text-sm text-muted-foreground">
            Choose when this recording started. Analytics timestamps will be anchored to that window.
          </p>

          {loadingDuration && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader className="w-4 h-4 animate-spin" />
              Loading video duration…
            </div>
          )}

          {durationError && (
            <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-800 dark:text-amber-300">
              {durationError}
            </div>
          )}

          {durationSeconds !== null && !loadingDuration && (
            <p className="text-sm text-foreground">
              Duration: <span className="font-medium">{durationSeconds.toFixed(1)}s</span>
            </p>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                <Calendar className="h-3.5 w-3.5" />
                Start date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                disabled={processing}
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 [color-scheme:dark] disabled:opacity-60"
              />
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                <Clock className="h-3.5 w-3.5" />
                Start time
              </label>
              <input
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                disabled={processing}
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 [color-scheme:dark] disabled:opacity-60"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                <Calendar className="h-3.5 w-3.5" />
                End date
              </label>
              <input
                type="date"
                value={endFields?.date ?? ''}
                readOnly
                disabled
                className="w-full rounded-lg border border-border bg-muted/40 px-3 py-2 text-sm text-muted-foreground [color-scheme:dark]"
              />
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                <Clock className="h-3.5 w-3.5" />
                End time
              </label>
              <input
                type="time"
                value={endFields?.time ?? ''}
                readOnly
                disabled
                className="w-full rounded-lg border border-border bg-muted/40 px-3 py-2 text-sm text-muted-foreground [color-scheme:dark]"
              />
            </div>
          </div>

          {statusMessage && !error && (
            <div className="rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-foreground">
              {statusMessage}
            </div>
          )}

          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-700 dark:text-red-400">
              {error}
            </div>
          )}
        </div>

        <div className="flex items-center justify-end gap-2 px-6 py-4 border-t border-border">
          <button
            type="button"
            onClick={onClose}
            disabled={processing}
            className="px-4 py-2 rounded border border-border text-sm hover:bg-muted disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={processing || loadingDuration}
            className="px-4 py-2 rounded bg-primary text-primary-foreground text-sm hover:bg-primary/90 disabled:opacity-60"
          >
            {processing ? 'Processing…' : 'Process Video'}
          </button>
        </div>
      </div>
    </div>
  );
}
