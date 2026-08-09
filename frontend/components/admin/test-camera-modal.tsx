'use client';

import { useEffect, useState } from 'react';
import { X, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import type { AdminCamera } from '@/lib/types';
import { testCamera, getCameraSnapshotUrl } from '@/lib/api/cameras';
import { resolveSnapshotHint, SNAPSHOT_HINT_MESSAGES } from '@/lib/snapshot-preview-hint';
import { ACTION_STATUS_COLORS } from '@/lib/constants';

type TestState = 'idle' | 'testing' | 'success' | 'error';

interface TestCameraModalProps {
  camera?: AdminCamera;
  isOpen: boolean;
  onClose: () => void;
  onTestComplete?: (cameraId: string, status: AdminCamera['status']) => void;
}

export function TestCameraModal({ camera, isOpen, onClose, onTestComplete }: TestCameraModalProps) {
  const [state, setState] = useState<TestState>('idle');
  const [error, setError] = useState<string>('');
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [detectedResolution, setDetectedResolution] = useState<string>('—');
  const [detectedFps, setDetectedFps] = useState<number | null>(null);
  const [previewUnavailable, setPreviewUnavailable] = useState(false);
  const [testedCameraStatus, setTestedCameraStatus] = useState<AdminCamera['status'] | undefined>(
    camera?.status,
  );

  const snapshotUrl =
    state === 'success' && camera
      ? getCameraSnapshotUrl(camera.id, { fresh: camera.sourceType === 'live' })
      : null;

  useEffect(() => {
    if (!isOpen || !camera) {
      return;
    }

    let cancelled = false;

    async function runTest() {
      setState('testing');
      setError('');
      setLatencyMs(null);
      setDetectedResolution('—');
      setDetectedFps(null);
      setPreviewUnavailable(false);
      setTestedCameraStatus(camera!.status);

      try {
        const result = await testCamera(camera!.id);
        if (cancelled) return;

        if (result.status === 'error') {
          setError(result.error);
          setState('error');
          if (result.camera_status) {
            setTestedCameraStatus(result.camera_status);
            onTestComplete?.(camera!.id, result.camera_status);
          }
          return;
        }

        setLatencyMs(result.latency_ms);
        setDetectedResolution(result.resolution);
        setDetectedFps(result.fps);
        setState('success');
        if (result.camera_status) {
          setTestedCameraStatus(result.camera_status);
          onTestComplete?.(camera!.id, result.camera_status);
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Camera test failed');
        setState('error');
      }
    }

    runTest();

    return () => {
      cancelled = true;
    };
  }, [isOpen, camera]);

  if (!isOpen || !camera) return null;

  const snapshotHint =
    state === 'success'
      ? resolveSnapshotHint(testedCameraStatus, camera.sourceType, previewUnavailable)
      : null;

  const handleClose = () => {
    setState('idle');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-md bg-card border border-border rounded-lg shadow-lg overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">Test Camera</h2>
          <button
            onClick={handleClose}
            className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Camera</p>
            <p className="font-semibold text-foreground">{camera.name}</p>
            <p className="text-xs text-muted-foreground">{camera.rtspUrl}</p>
          </div>

          {state === 'testing' && (
            <div className="flex flex-col items-center justify-center py-8 space-y-4">
              <div className="relative w-16 h-16">
                <Loader className="w-16 h-16 text-primary animate-spin" />
              </div>
              <div className="text-center">
                <p className="font-medium text-foreground">Testing connection...</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Calling POST /api/cameras/{camera.id}/test
                </p>
              </div>
            </div>
          )}

          {state === 'success' && (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <CheckCircle className={`w-6 h-6 ${ACTION_STATUS_COLORS.positiveIcon}`} />
                <div>
                  <p className="font-semibold text-foreground">Connection successful</p>
                  <p className="text-sm text-muted-foreground">Backend stream probe succeeded</p>
                </div>
              </div>

              <div className="rounded-lg border border-border overflow-hidden bg-muted/30 relative">
                {snapshotUrl && !previewUnavailable ? (
                  <img
                    src={snapshotUrl}
                    alt={`${camera.name} snapshot`}
                    className="w-full aspect-video object-cover"
                    onError={() => setPreviewUnavailable(true)}
                  />
                ) : snapshotHint ? (
                  <div className="px-4 py-6 text-center">
                    <p className="text-sm font-medium text-foreground">
                      {SNAPSHOT_HINT_MESSAGES[snapshotHint]}
                    </p>
                  </div>
                ) : (
                  <div className="px-4 py-6 text-center">
                    <p className="text-sm font-medium text-foreground">Snapshot unavailable</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Could not load the camera snapshot.
                    </p>
                  </div>
                )}
              </div>

              <div className="bg-muted/50 rounded-lg p-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Detected Resolution:</span>
                  <span className="font-medium text-foreground">{detectedResolution}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Frame Rate:</span>
                  <span className="font-medium text-foreground">
                    {detectedFps != null ? `${detectedFps} FPS` : '—'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Latency:</span>
                  <span className="font-medium text-foreground">
                    {latencyMs != null ? `${latencyMs}ms` : '—'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {state === 'error' && (
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <AlertCircle className={`w-6 h-6 ${ACTION_STATUS_COLORS.negativeIcon} flex-shrink-0 mt-0.5`} />
                <div>
                  <p className="font-semibold text-foreground">Test failed</p>
                  <p className="text-sm text-muted-foreground mt-1">{error}</p>
                </div>
              </div>

              <div className={`${ACTION_STATUS_COLORS.negativePanel} rounded-lg p-3`}>
                <p className="text-xs text-red-700 dark:text-red-400">
                  {camera.sourceType === 'recorded' ? (
                    <>
                      <strong>Recorded source:</strong>{' '}
                      {SNAPSHOT_HINT_MESSAGES.source_unavailable}
                    </>
                  ) : (
                    <>
                      <strong>Troubleshooting:</strong> Check the RTSP URL, verify network connectivity,
                      and ensure the camera is powered on.
                    </>
                  )}
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 px-6 py-4 border-t border-border bg-muted/40">
          <button
            onClick={handleClose}
            className="px-4 py-2 rounded bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            {state === 'testing' ? 'Close' : 'Done'}
          </button>
        </div>
      </div>
    </div>
  );
}
