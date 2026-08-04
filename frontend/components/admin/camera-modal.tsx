'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { X } from 'lucide-react';
import type { AdminCamera, AnalyticsModule, CameraSourceType, Resolution } from '@/lib/types';
import type { CreateCameraData } from '@/lib/api/cameras';
import {
  ANALYTICS_MODULES_LABELS,
  ensureStoresLoaded,
  getCameraProcessStatus,
  processCameraVideo,
  STORES,
} from '@/lib/api/cameras';

interface CameraModalProps {
  camera?: AdminCamera;
  isOpen: boolean;
  onClose: () => void;
  onSave: (camera: AdminCamera | CreateCameraData) => void | Promise<void>;
  onProcessed?: (camera: AdminCamera) => void;
}

const ANALYTICS_MODULES: AnalyticsModule[] = [
  'entry-exit',
  'occupancy',
  'zones',
  'dwell',
  'heatmap',
  'queue',
];

const RESOLUTIONS: Resolution[] = ['1080p', '2k', '4k'];

type CameraFormFields = {
  name: string;
  store: string;
  location: string;
  status: AdminCamera['status'];
  sourceType: CameraSourceType;
  resolution: Resolution;
  fps: number;
  rtspUrl: string;
  cameraType: AdminCamera['cameraType'];
  analyticsModules: AnalyticsModule[];
  enabled: boolean;
};

function buildEmptyForm(storeName: string): CameraFormFields {
  return {
    name: '',
    store: storeName,
    location: '',
    status: 'online',
    sourceType: 'live',
    resolution: '2k',
    fps: 30,
    rtspUrl: '',
    cameraType: 'fixed',
    // Matches the backend's CameraCreate default (all supported modules) — a
    // new camera previously defaulted to an empty module list here, silently
    // disabling every analytics module until an admin manually checked every box.
    analyticsModules: [...ANALYTICS_MODULES],
    enabled: true,
  };
}

export function CameraModal({ camera, isOpen, onClose, onSave, onProcessed }: CameraModalProps) {
  const [formData, setFormData] = useState<CameraFormFields>(buildEmptyForm(''));
  const [storesLoading, setStoresLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [processing, setProcessing] = useState(false);
  const [processMessage, setProcessMessage] = useState('');

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    let cancelled = false;
    setValidationError('');
    setProcessMessage('');

    async function hydrateForm() {
      setStoresLoading(true);
      try {
        await ensureStoresLoaded();
        if (cancelled) return;
        if (camera) {
          setFormData({
            name: camera.name,
            store: camera.store,
            location: camera.location,
            status: camera.status,
            sourceType: camera.sourceType,
            resolution: camera.resolution,
            fps: camera.fps,
            rtspUrl: camera.rtspUrl,
            cameraType: camera.cameraType,
            analyticsModules: camera.analyticsModules,
            enabled: camera.enabled,
          });
        } else {
          setFormData(buildEmptyForm(STORES[0] ?? ''));
        }
      } finally {
        if (!cancelled) {
          setStoresLoading(false);
        }
      }
    }

    hydrateForm();
    return () => {
      cancelled = true;
    };
  }, [isOpen, camera]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError('');

    const name = formData.name.trim();
    const store = formData.store.trim();
    const location = formData.location.trim();
    const rtspUrl = formData.rtspUrl.trim();
    const isLive = formData.sourceType === 'live';

    if (!name || !store || !location || !rtspUrl) {
      setValidationError(
        isLive
          ? 'Camera name, store, location, and stream URL are required.'
          : 'Camera name, store, location, and video file path are required.',
      );
      return;
    }

    if (storesLoading) {
      setValidationError('Store list is still loading. Please wait a moment.');
      return;
    }

    const shared = {
      name,
      store,
      location,
      rtspUrl,
      sourceType: formData.sourceType,
      status: formData.status,
      resolution: formData.resolution,
      fps: formData.fps,
      cameraType: formData.cameraType,
      analyticsModules: formData.analyticsModules,
      enabled: formData.enabled,
    };

    setSubmitting(true);
    try {
      if (camera) {
        await onSave({ ...shared, id: camera.id });
      } else {
        await onSave(shared);
      }
      onClose();
    } catch (err) {
      setValidationError(
        err instanceof Error ? err.message : 'Failed to save camera',
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleProcessVideo = async () => {
    if (!camera || camera.sourceType !== 'recorded') return;
    setProcessing(true);
    setProcessMessage('Starting video processing…');
    setValidationError('');
    try {
      let status = await processCameraVideo(camera.id);
      while (status.status === 'running') {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        status = await getCameraProcessStatus(camera.id);
        setProcessMessage(status.message ?? 'Processing video…');
      }
      if (status.status === 'failed') {
        setValidationError(status.message ?? 'Video processing failed');
        return;
      }
      setProcessMessage('Video processed successfully.');
      onProcessed?.({
        ...camera,
        lastProcessedAt: status.finished_at ?? new Date().toISOString(),
      });
    } catch (err) {
      setValidationError(
        err instanceof Error ? err.message : 'Failed to process video',
      );
    } finally {
      setProcessing(false);
    }
  };

  const toggleModule = (module: AnalyticsModule) => {
    const modules = formData.analyticsModules || [];
    setFormData({
      ...formData,
      analyticsModules: modules.includes(module)
        ? modules.filter((m) => m !== module)
        : [...modules, module],
    });
  };

  if (!isOpen) return null;

  const isRecorded = formData.sourceType === 'recorded';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-2xl max-h-[90vh] bg-card border border-border rounded-lg shadow-lg overflow-y-auto">
        <div className="sticky top-0 flex items-center justify-between px-6 py-4 border-b border-border bg-card">
          <h2 className="text-lg font-semibold text-foreground">
            {camera ? 'Edit Camera' : 'Add Camera'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {validationError && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-700 dark:text-red-400">
              {validationError}
            </div>
          )}
          {processMessage && !validationError && (
            <div className="rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-foreground">
              {processMessage}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Source Type
            </label>
            <div className="inline-flex rounded-lg border border-border overflow-hidden">
              <button
                type="button"
                onClick={() => setFormData({ ...formData, sourceType: 'live' })}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  !isRecorded
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:text-foreground'
                }`}
              >
                Live Stream
              </button>
              <button
                type="button"
                onClick={() => setFormData({ ...formData, sourceType: 'recorded' })}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  isRecorded
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:text-foreground'
                }`}
              >
                Recorded Video
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Camera Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 bg-muted border border-border rounded text-foreground"
              placeholder="e.g., Entrance - Left"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Store</label>
              <select
                value={formData.store}
                onChange={(e) => setFormData({ ...formData, store: e.target.value })}
                disabled={storesLoading || STORES.length === 0}
                className="w-full px-3 py-2 bg-muted border border-border rounded text-foreground disabled:opacity-50"
              >
                {STORES.length === 0 ? (
                  <option value="">No stores available</option>
                ) : (
                  STORES.map((store) => (
                    <option key={store} value={store}>
                      {store}
                    </option>
                  ))
                )}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Location
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full px-3 py-2 bg-muted border border-border rounded text-foreground"
                placeholder="e.g., Main entrance, left side"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              {isRecorded ? 'Video File Path' : 'RTSP URL'}
            </label>
            <input
              type="text"
              value={formData.rtspUrl}
              onChange={(e) => setFormData({ ...formData, rtspUrl: e.target.value })}
              className="w-full px-3 py-2 bg-muted border border-border rounded text-foreground"
              placeholder={
                isRecorded
                  ? 'e.g., sample-data/town.mp4'
                  : 'e.g., rtsp://192.168.1.100:554/stream'
              }
            />
          </div>

          {camera && isRecorded && (
            <div className="rounded-lg border border-border bg-muted/30 p-4 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <p className="text-sm font-medium text-foreground">Recorded video processing</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {camera.lastProcessedAt
                      ? `Last processed: ${new Date(camera.lastProcessedAt).toLocaleString()}`
                      : 'Not yet processed'}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Link
                    href="/analytics/occupancy"
                    className="text-sm text-primary hover:underline"
                  >
                    View analytics
                  </Link>
                  <button
                    type="button"
                    onClick={handleProcessVideo}
                    disabled={processing}
                    className="px-3 py-1.5 rounded bg-primary text-primary-foreground text-sm hover:bg-primary/90 disabled:opacity-60"
                  >
                    {processing ? 'Processing…' : 'Process Video'}
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Camera Type
              </label>
              <select
                value={formData.cameraType}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    cameraType: e.target.value as 'fixed' | 'ptz',
                  })
                }
                className="w-full px-3 py-2 bg-muted border border-border rounded text-foreground"
              >
                <option value="fixed">Fixed</option>
                <option value="ptz">PTZ</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Resolution
              </label>
              <select
                value={formData.resolution}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    resolution: e.target.value as Resolution,
                  })
                }
                className="w-full px-3 py-2 bg-muted border border-border rounded text-foreground"
              >
                {RESOLUTIONS.map((res) => (
                  <option key={res} value={res}>
                    {res}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">FPS</label>
              <input
                type="number"
                min="1"
                max="60"
                value={formData.fps}
                onChange={(e) => setFormData({ ...formData, fps: Number(e.target.value) })}
                className="w-full px-3 py-2 bg-muted border border-border rounded text-foreground"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-3">
              Analytics Modules
            </label>
            <div className="grid grid-cols-2 gap-3">
              {ANALYTICS_MODULES.map((module) => (
                <label key={module} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.analyticsModules.includes(module)}
                    onChange={() => toggleModule(module)}
                    className="w-4 h-4 rounded border-border bg-muted accent-primary"
                  />
                  <span className="text-sm text-foreground">
                    {ANALYTICS_MODULES_LABELS[module]}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-border">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded bg-muted text-foreground hover:bg-muted/80 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || storesLoading}
              className="px-4 py-2 rounded bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-60"
            >
              {submitting
                ? 'Saving…'
                : camera
                  ? 'Update Camera'
                  : 'Add Camera'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
