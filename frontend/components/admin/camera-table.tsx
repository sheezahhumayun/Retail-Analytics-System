'use client';

import Link from 'next/link';
import { Trash2, Edit2, Check, X, Zap, Play } from 'lucide-react';
import type { AdminCamera } from '@/lib/types';
import {
  ANALYTICS_MODULES_LABELS,
  getStatusColor,
  getStatusLabel,
  processCameraVideo,
  getCameraProcessStatus,
} from '@/lib/api/cameras';
import { ACTION_STATUS_COLORS } from '@/lib/constants';
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

export function CameraTable({
  cameras,
  onEdit,
  onDelete,
  onToggleEnabled,
  onTestCamera,
  onCameraUpdated,
}: CameraTableProps) {
  const [processingId, setProcessingId] = useState<string | null>(null);

  const handleProcess = async (camera: AdminCamera) => {
    setProcessingId(camera.id);
    try {
      let status = await processCameraVideo(camera.id);
      while (status.status === 'running') {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        status = await getCameraProcessStatus(camera.id);
      }
      if (status.status === 'completed') {
        onCameraUpdated?.({
          ...camera,
          lastProcessedAt: status.finished_at ?? new Date().toISOString(),
        });
      }
    } finally {
      setProcessingId(null);
    }
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
                        {new Date(camera.lastProcessedAt).toLocaleString()}
                      </p>
                    )}
                    <Link
                      href="/analytics/occupancy"
                      className="text-xs text-primary hover:underline block"
                    >
                      Analytics →
                    </Link>
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
                      disabled={processingId === camera.id}
                      title="Process video"
                      className="p-1.5 hover:bg-muted rounded transition-colors text-muted-foreground hover:text-foreground disabled:opacity-50"
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
    </div>
  );
}
