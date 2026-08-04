'use client';

import { useEffect, useMemo, useState } from 'react';
import { DashboardShell } from '@/components/dashboard/dashboard-shell';
import { HeatmapCanvas } from '@/components/heatmap/heatmap-canvas';
import { HeatmapControls } from '@/components/heatmap/heatmap-controls';
import { HeatmapLegend } from '@/components/heatmap/heatmap-legend';
import {
  getHeatmap,
  getHeatmapCameras,
} from '@/lib/api/analytics';
import { ApiClientError } from '@/lib/api/client';
import {
  filterHeatmapCameras,
} from '@/lib/scope/scope-filters';
import { useScope } from '@/lib/scope/ScopeContext';
import type { FloorZone, HeatBlob, HeatmapCamera } from '@/lib/types';

/** UTC calendar date matching demo seed end (`compute_demo_date_range().end`). */
function mostRecentSeedDate(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function HeatmapPage() {
  const { storeId, cameraId, storeCameraIds } = useScope();
  const defaultDate = mostRecentSeedDate();

  const [allCameras, setAllCameras] = useState<HeatmapCamera[]>([]);
  const [date, setDate] = useState(defaultDate);
  const [timeFrom, setTimeFrom] = useState('09:00');
  const [timeTo, setTimeTo] = useState('18:00');
  const [opacity, setOpacity] = useState(0.72);
  const [blobs, setBlobs] = useState<HeatBlob[]>([]);
  const [floorZones, setFloorZones] = useState<FloorZone[]>([]);
  const [loading, setLoading] = useState(true);
  const [emptyMessage, setEmptyMessage] = useState<string | null>(null);

  const scopedCameras = useMemo(
    () => filterHeatmapCameras(allCameras, cameraId, storeCameraIds),
    [allCameras, cameraId, storeCameraIds],
  );

  const allowedCameraIds = useMemo(
    () => scopedCameras.map((camera) => camera.id),
    [scopedCameras],
  );

  useEffect(() => {
    let cancelled = false;

    async function loadMeta() {
      try {
        const cameraList = await getHeatmapCameras();
        if (!cancelled) {
          setAllCameras(cameraList);
        }
      } catch {
        if (!cancelled) {
          setAllCameras([]);
        }
      }
    }

    loadMeta();
    return () => {
      cancelled = true;
    };
  }, [storeId]);

  useEffect(() => {
    if (!cameraId) {
      setLoading(false);
      setBlobs([]);
      setFloorZones([]);
      setEmptyMessage('Select a camera to view heatmap data.');
      return;
    }

    let cancelled = false;

    async function loadHeatmap() {
      setLoading(true);
      setEmptyMessage(null);
      try {
        const result = await getHeatmap({
          camera_id: cameraId!,
          date,
          from_time: timeFrom,
          to_time: timeTo,
        });
        if (!cancelled) {
          setBlobs(result.blobs);
          setFloorZones(result.floor_zones);
          setEmptyMessage(
            result.blobs.length === 0
              ? `No heatmap density for camera '${cameraId!}' on ${date}.`
              : null,
          );
        }
      } catch (err) {
        if (!cancelled) {
          setBlobs([]);
          setFloorZones([]);
          if (err instanceof ApiClientError && err.status === 404) {
            setEmptyMessage(
              err.message ||
                `No heatmap data for camera '${cameraId!}' on ${date}.`,
            );
          } else {
            setEmptyMessage(
              err instanceof Error
                ? err.message
                : 'Failed to load heatmap data.',
            );
          }
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadHeatmap();
    return () => {
      cancelled = true;
    };
  }, [cameraId, date, timeFrom, timeTo]);

  return (
    <DashboardShell scopeBarConfig={{ showZone: false, showCameraAllOption: false }}>
      <div className="flex flex-col gap-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold text-foreground text-balance">Store Heatmap</h1>
            <p className="mt-0.5 text-sm text-muted-foreground">
              Visitor density across the floor plan — select a camera, date, and time range.
            </p>
          </div>
          <div className="shrink-0 rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground">
            Updated just now
          </div>
        </div>

        <HeatmapControls
          cameras={scopedCameras}
          selectedCamera={cameraId || ''}
          onCameraChange={(newCamera) => {
            // Note: This is for HeatmapControls backward compatibility
            // Camera selection is now handled via the top bar scope selector
          }}
          date={date}
          onDateChange={setDate}
          timeFrom={timeFrom}
          onTimeFromChange={setTimeFrom}
          timeTo={timeTo}
          onTimeToChange={setTimeTo}
          opacity={opacity}
          onOpacityChange={setOpacity}
        />

        {loading ? (
          <div className="flex aspect-[16/9] items-center justify-center rounded-lg border border-border bg-card">
            <div className="text-center">
              <div className="inline-block relative w-10 h-10 mb-3">
                <div className="absolute inset-0 border-4 border-transparent border-t-primary border-r-primary rounded-full animate-spin" />
              </div>
              <p className="text-sm text-muted-foreground">Loading heatmap…</p>
            </div>
          </div>
        ) : emptyMessage ? (
          <div className="flex aspect-[16/9] items-center justify-center rounded-lg border border-dashed border-border bg-card">
            <div className="max-w-md px-6 text-center">
              <p className="text-sm font-medium text-foreground">No heatmap data</p>
              <p className="mt-1.5 text-sm text-muted-foreground">{emptyMessage}</p>
              <p className="mt-3 text-xs text-muted-foreground">
                Try another date in the seeded range, or a different camera / time window.
              </p>
            </div>
          </div>
        ) : (
          <HeatmapCanvas blobs={blobs} zones={floorZones} opacity={opacity} />
        )}

        <HeatmapLegend />
      </div>
    </DashboardShell>
  );
}
