'use client';

import { useRef, useState, useCallback, useEffect } from 'react';
import { Camera, Save, CheckCircle, AlertCircle } from 'lucide-react';
import { DashboardShell } from '@/components/dashboard/dashboard-shell';
import { EditorToolbar } from '@/components/admin/zones-lines/editor-toolbar';
import { ShapesSidebar } from '@/components/admin/zones-lines/shapes-sidebar';
import { ZonesLinesCanvas, triggerFinishZone } from '@/components/admin/zones-lines/zones-lines-canvas';
import {
  deleteZone,
  getAllShapes,
  getCamerasList,
  getShapesForCamera,
  syncCameraShapes,
} from '@/lib/api/zones';
import { deleteCountingLine } from '@/lib/api/lines';
import { getCameraMeta } from '@/lib/api/cameras';
import type { Shape } from '@/lib/types';
import type { DrawMode, CameraSourceType, CameraStatus } from '@/lib/types';

const SELECTED_CAMERA_STORAGE_KEY = 'admin-zones-lines-selected-camera';

function readStoredCameraId(
  cameras: { id: string; label: string }[],
): string {
  if (typeof window === 'undefined') {
    return cameras[0]?.id ?? '';
  }

  const stored = sessionStorage.getItem(SELECTED_CAMERA_STORAGE_KEY);
  if (stored && cameras.some((camera) => camera.id === stored)) {
    return stored;
  }

  return cameras[0]?.id ?? '';
}

function persistSelectedCamera(cameraId: string) {
  if (typeof window === 'undefined' || !cameraId) return;
  sessionStorage.setItem(SELECTED_CAMERA_STORAGE_KEY, cameraId);
}

export default function AdminZonesLinesPage() {
  const canvasElRef = useRef<HTMLCanvasElement | null>(null);
  const shapesRef = useRef<Shape[]>([]);
  const savedShapesRef = useRef<Shape[]>([]);
  const selectedCameraRef = useRef('');

  const [camerasList, setCamerasList] = useState<{ id: string; label: string; status: CameraStatus; sourceType: CameraSourceType }[]>([]);
  const [selectedCamera, setSelectedCamera] = useState('');
  const [shapes, setShapes] = useState<Shape[]>([]);
  const [savedShapes, setSavedShapes] = useState<Shape[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [mode, setMode] = useState<DrawMode>('select');
  const [canFinish, setCanFinish] = useState(false);
  const [selectedShapeId, setSelectedShapeId] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [saveError, setSaveError] = useState('');

  useEffect(() => {
    shapesRef.current = shapes;
  }, [shapes]);

  useEffect(() => {
    savedShapesRef.current = savedShapes;
  }, [savedShapes]);

  useEffect(() => {
    selectedCameraRef.current = selectedCamera;
  }, [selectedCamera]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const cameras = await getCamerasList();
        const cameraId = readStoredCameraId(cameras);
        persistSelectedCamera(cameraId);

        const allShapes = await getAllShapes({ includeDisabled: true });
        if (!cancelled) {
          setCamerasList(cameras);
          setSelectedCamera(cameraId);
          setShapes(allShapes);
          setSavedShapes(allShapes);
          setLoadError('');
        }
      } catch (err) {
        if (!cancelled) {
          setLoadError(err instanceof Error ? err.message : 'Failed to load shapes');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedCamera) return;

    let cancelled = false;
    getCameraMeta(selectedCamera).then((meta) => {
      if (cancelled || !meta) return;
      setCamerasList((prev) =>
        prev.map((camera) =>
          camera.id === selectedCamera
            ? { ...camera, status: meta.status, sourceType: meta.sourceType }
            : camera,
        ),
      );
    });

    return () => {
      cancelled = true;
    };
  }, [selectedCamera]);

  const selectedCameraMeta = camerasList.find((camera) => camera.id === selectedCamera);

  const cameraShapes = shapes.filter((s) => s.cameraId === selectedCamera);
  const editableCameraShapes = cameraShapes.filter((s) => s.status !== 'disabled');

  const handleShapesChange = useCallback((updated: Shape[]) => {
    const cameraId =
      updated.find((shape) => shape.cameraId)?.cameraId ??
      selectedCameraRef.current;
    if (!cameraId) return;

    setShapes((prev) => {
      const other = prev.filter((shape) => shape.cameraId !== cameraId);
      return [...other, ...updated];
    });
  }, []);

  async function handleDeleteShape(id: string) {
    const shape = shapesRef.current.find((item) => item.id === id);
    if (!shape || shape.status === 'disabled') return;

    try {
      if (shape.kind === 'zone') {
        await deleteZone(id);
      } else {
        await deleteCountingLine(id);
      }
      const cameraId = selectedCameraRef.current;
      if (cameraId) {
        const refreshedForCamera = await getShapesForCamera(cameraId, { includeDisabled: true });
        const refreshedAll = await getAllShapes({ includeDisabled: true });
        setShapes(refreshedAll);
        setSavedShapes(refreshedAll);
        if (selectedShapeId === id) setSelectedShapeId(null);
        void refreshedForCamera;
      }
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to delete shape');
      setSaveState('error');
    }
  }

  async function handleSave() {
    const cameraId = selectedCameraRef.current;
    if (!cameraId) return;

    const current = shapesRef.current.filter((shape) => shape.cameraId === cameraId);
    const baseline = savedShapesRef.current.filter((shape) => shape.cameraId === cameraId);

    setSaveState('saving');
    setSaveError('');

    try {
      await syncCameraShapes(cameraId, current, baseline);

      const refreshedForCamera = await getShapesForCamera(cameraId, { includeDisabled: true });
      const refreshedAll = await getAllShapes({ includeDisabled: true });

      const missingNew = current.filter(
        (shape) =>
          !baseline.some((entry) => entry.id === shape.id) &&
          !refreshedForCamera.some((entry) => entry.id === shape.id),
      );
      if (missingNew.length > 0) {
        throw new Error(
          `Server did not return ${missingNew.length} newly saved shape(s). Check the Network tab for POST /api/zones failures.`,
        );
      }

      setShapes(refreshedAll);
      setSavedShapes(refreshedAll);
      persistSelectedCamera(cameraId);
      setSaveState('saved');
      setTimeout(() => setSaveState('idle'), 2500);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save shapes');
      setSaveState('error');
    }
  }

  return (
    <DashboardShell>
      <div className="space-y-5 max-w-[1400px] mx-auto">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Zones &amp; Lines</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Draw zone polygons and counting lines on a camera frame
            </p>
          </div>

          <button
            type="button"
            onClick={handleSave}
            disabled={saveState === 'saving' || loading || !selectedCamera}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors border bg-primary text-primary-foreground border-primary hover:bg-primary/90 disabled:opacity-60"
          >
            {saveState === 'saved' ? (
              <><CheckCircle className="h-4 w-4" /> Saved</>
            ) : saveState === 'saving' ? (
              <><span className="h-4 w-4 rounded-full border-2 border-primary-foreground/40 border-t-primary-foreground animate-spin" /> Saving…</>
            ) : (
              <><Save className="h-4 w-4" /> Save</>
            )}
          </button>
        </div>

        {saveState === 'error' && saveError && (
          <div className="flex items-start gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-700 dark:text-red-400">
            <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <span>{saveError}</span>
          </div>
        )}

        <div className="flex flex-wrap items-end gap-3 rounded-xl border border-border bg-card px-5 py-4">
          <div className="flex flex-col gap-1.5 min-w-[280px]">
            <label className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <Camera className="h-3.5 w-3.5" />
              Camera
            </label>
            <div className="relative">
              <select
                value={selectedCamera}
                onChange={(e) => {
                  const nextCamera = e.target.value;
                  setSelectedCamera(nextCamera);
                  persistSelectedCamera(nextCamera);
                  setMode('select');
                  setSelectedShapeId(null);
                }}
                disabled={loading}
                className="w-full appearance-none rounded-lg border border-border bg-background px-3 py-2 pr-8 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 cursor-pointer"
              >
                {camerasList.map((c) => (
                  <option key={c.id} value={c.id}>{c.label}</option>
                ))}
              </select>
              <span className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
            </div>
          </div>

          <div className="h-9 w-px bg-border hidden sm:block self-end mb-0.5" />

          <EditorToolbar
            mode={mode}
            onModeChange={setMode}
            canFinish={canFinish}
            onFinish={() => triggerFinishZone(canvasElRef.current)}
          />
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-24 rounded-xl border border-border bg-card">
            <div className="text-center">
              <div className="inline-block relative w-10 h-10 mb-3">
                <div className="absolute inset-0 border-4 border-transparent border-t-primary border-r-primary rounded-full animate-spin" />
              </div>
              <p className="text-sm text-muted-foreground">Loading shapes…</p>
            </div>
          </div>
        ) : loadError ? (
          <div className="flex items-center justify-center py-24 rounded-xl border border-dashed border-border bg-card">
            <p className="text-sm text-muted-foreground">{loadError}</p>
          </div>
        ) : (
          <div className="flex gap-5 items-start">
            <div className="flex-1 min-w-0">
              <ZonesLinesCanvas
                cameraId={selectedCamera}
                cameraStatus={selectedCameraMeta?.status}
                cameraSourceType={selectedCameraMeta?.sourceType}
                shapes={editableCameraShapes}
                onShapesChange={handleShapesChange}
                mode={mode}
                onModeChange={setMode}
                onCanFinish={setCanFinish}
              />

              <div className="mt-3 flex flex-wrap gap-4 text-xs text-muted-foreground">
                <span className="flex items-center gap-1.5">
                  <span className="inline-block h-3 w-3 rounded-sm" style={{ background: '#22d3ee' }} />
                  Entrance zone
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="inline-block h-3 w-3 rounded-sm" style={{ background: '#f59e0b' }} />
                  Checkout / Queue zone
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="inline-block h-3 w-3 rounded-sm" style={{ background: '#a78bfa' }} />
                  General zone
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="inline-block h-8 w-0.5 border-l-2 border-dashed" style={{ borderColor: '#34d399' }} />
                  Counting line (arrow = inside)
                </span>
              </div>
            </div>

            <ShapesSidebar
              shapes={cameraShapes}
              selectedId={selectedShapeId}
              onSelect={setSelectedShapeId}
              onDelete={handleDeleteShape}
            />
          </div>
        )}

        <p className="text-xs text-muted-foreground">
          Tip: Double-click the canvas to close a polygon, or click near the first vertex when 3+ points are placed.
        </p>
      </div>
    </DashboardShell>
  );
}
