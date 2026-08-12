'use client';

import { Trash2, Edit2, Check, X, Zap, Play } from 'lucide-react';
import type { AdminCamera } from '@/lib/types';
import { ProcessingRunPreviewModal } from '@/components/admin/processing-run-preview-modal';
import { ProcessVideoModal } from '@/components/admin/process-video-modal';
import {
  ANALYTICS_MODULES_LABELS,
  getStatusColor,
  getStatusLabel,
} from '@/lib/api/cameras';
import { ApiClientError } from '@/lib/api/client';
import { ACTION_STATUS_COLORS } from '@/lib/constants';
import { formatUtcDateTime } from '@/lib/format-datetime';
import { useState } from 'react';

interface CameraTableProps {
  cameras: AdminCamera[];
  onEdit: (camera: AdminCamera) => void;
  onDelete: (cameraId: string) => void;
  onToggleEnabled: (cameraId: string, enabled: boolean) => void;
  onTestCamera: (camera: AdminCamera) => void;
  onCameraUpdated?: (camera: AdminCamera) => void;
}

function RecordedBadge({ camera }: { camera: AdminCamera }) {
  const processed = Boolean(camera.lastProcessedAt);
  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
        processed
          ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400'
          : 'bg-amber-500/15 text-amber-700 dark:text-amber-400'
      }`}
    >
      Recorded — {processed ? 'processed' : 'not yet processed'}
    </span>
  );
}

function formatProcessErrorMessage(message: string | null | undefined): string {
  if (!message) return 'Video processing failed';
  const trimmed = message.trim();
  const operational = trimmed.match(/(?:OperationalError|DetachedInstanceError|Error):[^\n]*/)?.[0];
  if (operational) return operational;
  const firstLine = trimmed.split('\n').find((line) => line.trim())?.trim();
  if (firstLine && firstLine.length <= 240) return firstLine;
  return trimmed.length > 240 ? `${trimmed.slice(0, 240)}…` : trimmed;
}

export function CameraTable({
  cameras,
  onEdit,
  onDelete,
  onToggleEnabled,
  onTestCamera,
  onCameraUpdated,
}: CameraTableProps) {
  const [processCamera, setProcessCamera] = useState<AdminCamera | null>(null);
  const [processError, setProcessError] = useState<{ cameraId: string; message: string } | null>(null);
  const [previewCamera, setPreviewCamera] = useState<AdminCamera | null>(null);

  const handleProcess = (camera: AdminCamera) => {
    setProcessError(null);
    setProcessCamera(camera);
  };

  return (
    <div className="overflow-x-auto border border-border rounded-lg bg-card">
      <table className="w-full text-sm">
        <thead className="border-b border-border bg-muted/40">
          <tr>
            <th className="px-4 py-3 text-left font-semibold text-foreground">Camera ID</th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">Name</th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">Source</th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">Store</th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">Location</th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">Status</th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">Resolution</th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">FPS</th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">Analytics</th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {cameras.map((camera) => (
            <tr key={camera.id} className="hover:bg-muted/40 transition-colors">
              <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{camera.id}</td>
              <td className="px-4 py-3 font-medium text-foreground">{camera.name}</td>
              <td className="px-4 py-3">
                {camera.sourceType === 'recorded' ? (
                  <div className="space-y-1">
                    <RecordedBadge camera={camera} />
                    {camera.lastProcessedAt && (
                      <p className="text-xs text-muted-foreground">
                        {formatUtcDateTime(camera.lastProcessedAt)}
                      </p>
                    )}
                    {camera.lastProcessedAt && (
                      <button
                        type="button"
                        onClick={() => setPreviewCamera(camera)}
                        className="text-xs text-primary hover:underline block text-left"
                      >
                        Preview last processed
                      </button>
                    )}
                    {processError?.cameraId === camera.id && (
                      <p className="text-xs text-destructive max-w-[14rem]" role="alert">
                        {processError.message}
                      </p>
                    )}
                  </div>
                ) : (
                  <span className="text-xs text-muted-foreground">Live stream</span>
                )}
              </td>
              <td className="px-4 py-3 text-foreground text-sm">{camera.store}</td>
              <td className="px-4 py-3 text-foreground text-sm">{camera.location}</td>
              <td className="px-4 py-3">
                <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(camera.status)}`}>
                  {getStatusLabel(camera.status)}
                </span>
              </td>
              <td className="px-4 py-3 text-foreground">{camera.resolution}</td>
              <td className="px-4 py-3 text-foreground">{camera.fps}</td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-1">
                  {camera.analyticsModules.map((mod) => (
                    <span
                      key={mod}
                      className="inline-flex items-center px-2 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium"
                    >
                      {ANALYTICS_MODULES_LABELS[mod]}
                    </span>
                  ))}
                </div>
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  {camera.sourceType === 'recorded' ? (
                    <button
                      onClick={() => handleProcess(camera)}
                      title="Process video"
                      className="p-1.5 hover:bg-muted rounded transition-colors text-muted-foreground hover:text-foreground"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  ) : (
                    <button
                      onClick={() => onTestCamera(camera)}
                      title="Test camera"
                      className="p-1.5 hover:bg-muted rounded transition-colors text-muted-foreground hover:text-foreground"
                    >
                      <Zap className="w-4 h-4" />
                    </button>
                  )}
                  <button
                    onClick={() => onToggleEnabled(camera.id, !camera.enabled)}
                    title={camera.enabled ? 'Disable camera' : 'Enable camera'}
                    className={`p-1.5 rounded transition-colors ${
                      camera.enabled
                        ? ACTION_STATUS_COLORS.negative
                        : ACTION_STATUS_COLORS.positive
                    }`}
                  >
                    {camera.enabled ? <X className="w-4 h-4" /> : <Check className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => onEdit(camera)}
                    title="Edit camera"
                    className="p-1.5 hover:bg-muted rounded transition-colors text-muted-foreground hover:text-foreground"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onDelete(camera.id)}
                    title="Delete camera"
                    className={`p-1.5 rounded transition-colors ${ACTION_STATUS_COLORS.negative}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {processCamera && (
        <ProcessVideoModal
          camera={processCamera}
          isOpen={Boolean(processCamera)}
          onClose={() => setProcessCamera(null)}
          onComplete={(updated) => {
            onCameraUpdated?.(updated);
            setProcessCamera(null);
          }}
        />
      )}
      {previewCamera && (
        <ProcessingRunPreviewModal
          cameraId={previewCamera.id}
          cameraName={previewCamera.name}
          isOpen={Boolean(previewCamera)}
          onClose={() => setPreviewCamera(null)}
        />
      )}
    </div>
  );
}
