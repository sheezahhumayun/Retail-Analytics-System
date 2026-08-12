'use client';

import { useEffect, useId, useState } from 'react';
import type { FloorZone, HeatBlob, CameraSourceType, CameraStatus } from '@/lib/types';
import { resolveSnapshotHint } from '@/lib/snapshot-preview-hint';
import { SnapshotPreviewHint } from '@/components/cameras/snapshot-preview-hint';

interface HeatmapCanvasProps {
  blobs: HeatBlob[];
  zones: FloorZone[];
  /** Optional camera snapshot URL for the background photo */
  snapshotUrl?: string | null;
  cameraStatus?: CameraStatus;
  cameraSourceType?: CameraSourceType;
  /** 0–1 global opacity of the heat overlay */
  opacity?: number;
}

function DecorativeFloorPlan() {
  return (
    <svg
      viewBox="0 0 100 56.25"
      preserveAspectRatio="none"
      className="absolute inset-0 h-full w-full"
      aria-hidden
    >
      <rect x="0" y="0" width="100" height="56.25" fill="#1a1c22" />
      <rect x="1" y="1" width="98" height="54.25" fill="none" stroke="#2e3142" strokeWidth="0.6" rx="0.5" />
      {[
        [20, 18], [50, 18], [80, 18],
        [20, 38], [50, 38], [80, 38],
      ].map(([cx, cy], i) => (
        <rect key={i} x={cx - 1} y={cy - 1} width="2" height="2" fill="#2e3142" rx="0.2" />
      ))}
      {[18, 36, 54, 72].map((x) => (
        <line key={`vl${x}`} x1={x} y1="3" x2={x} y2="53.25" stroke="#23253a" strokeWidth="0.25" strokeDasharray="1,1.5" />
      ))}
      {[14, 28, 42].map((y) => (
        <line key={`hl${y}`} x1="3" y1={y} x2="97" y2={y} stroke="#23253a" strokeWidth="0.25" strokeDasharray="1,1.5" />
      ))}
      <rect x="5" y="6" width="10" height="2.5" fill="#252840" rx="0.3" />
      <rect x="5" y="10" width="10" height="2.5" fill="#252840" rx="0.3" />
      <rect x="5" y="14" width="10" height="2.5" fill="#252840" rx="0.3" />
      <rect x="67" y="24" width="12" height="2" fill="#252840" rx="0.3" />
      <rect x="67" y="28" width="12" height="2" fill="#252840" rx="0.3" />
      <rect x="67" y="32" width="12" height="2" fill="#252840" rx="0.3" />
      <rect x="50" y="51" width="14" height="2" fill="#252840" rx="0.3" />
      <rect x="50" y="55" width="14" height="2" fill="none" />
      <rect x="20" y="3.5" width="16" height="2" fill="#252840" rx="0.3" />
      <rect x="40" y="3.5" width="16" height="2" fill="#252840" rx="0.3" />
      <rect x="60" y="3.5" width="16" height="2" fill="#252840" rx="0.3" />
      <rect x="44" y="54" width="12" height="1" fill="#1e3a5f" rx="0.2" />
      <line x1="44" y1="53.5" x2="44" y2="55.25" stroke="#2a5080" strokeWidth="0.4" />
      <line x1="56" y1="53.5" x2="56" y2="55.25" stroke="#2a5080" strokeWidth="0.4" />
    </svg>
  );
}

function polygonCentroid(points: { x: number; y: number }[]): { x: number; y: number } {
  let x = 0;
  let y = 0;
  for (const point of points) {
    x += point.x;
    y += point.y;
  }
  const count = points.length;
  return { x: x / count, y: y / count };
}

function pctYToViewBox(yPct: number): number {
  return (yPct / 100) * 56.25;
}

/**
 * Renders a store floor-plan grid with SVG radial-gradient heat blobs on top.
 * Zone overlays use polygon vertices in 0–100% frame space; heat blobs use their own viewBox.
 */
export function HeatmapCanvas({
  blobs,
  zones,
  snapshotUrl,
  cameraStatus,
  cameraSourceType,
  opacity = 0.72,
}: HeatmapCanvasProps) {
  const uid = useId().replace(/:/g, '');
  const [snapshotFailed, setSnapshotFailed] = useState(false);
  const showSnapshot = Boolean(snapshotUrl) && !snapshotFailed;

  useEffect(() => {
    setSnapshotFailed(false);
  }, [snapshotUrl]);

  const snapshotHint = resolveSnapshotHint(
    cameraStatus,
    cameraSourceType,
    !showSnapshot && Boolean(snapshotUrl),
  );

  return (
    <div className="relative w-full overflow-hidden rounded-xl" style={{ aspectRatio: '16/9' }}>

      {showSnapshot ? (
        <img
          src={snapshotUrl!}
          alt=""
          className="absolute inset-0 h-full w-full object-cover"
          aria-hidden
          onError={() => setSnapshotFailed(true)}
        />
      ) : (
        <DecorativeFloorPlan />
      )}

      {/* ── Zone boundary overlays ─────────────────────────────────── */}
      <svg
        viewBox="0 0 100 56.25"
        preserveAspectRatio="none"
        className="absolute inset-0 h-full w-full"
        aria-hidden
      >
        {zones.map((z) => {
          if (z.points.length < 3) {
            return null;
          }
          const pointsAttr = z.points
            .map((point) => `${point.x},${pctYToViewBox(point.y)}`)
            .join(' ');
          return (
            <polygon
              key={z.id}
              points={pointsAttr}
              fill="none"
              stroke="#3a4060"
              strokeWidth="0.35"
              strokeDasharray="1.5,1"
            />
          );
        })}

        {zones.map((z) => {
          if (z.points.length < 3) {
            return null;
          }
          const centroid = polygonCentroid(z.points);
          const lx = centroid.x;
          const ly = pctYToViewBox(centroid.y);
          return (
            <text
              key={`lbl-${z.id}`}
              x={lx}
              y={ly}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="2"
              fill="#5a6080"
              fontFamily="ui-sans-serif, system-ui, sans-serif"
              letterSpacing="0.1"
            >
              {z.label.toUpperCase()}
            </text>
          );
        })}
      </svg>

      {/* ── Heat overlay ────────────────────────────────────────────── */}
      <svg
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        className="absolute inset-0 h-full w-full pointer-events-none"
        style={{ opacity }}
        aria-hidden
      >
        <defs>
          {blobs.map((b) => (
            <radialGradient
              key={`grad-${uid}-${b.id}`}
              id={`grad-${uid}-${b.id}`}
              cx="50%" cy="50%"
              r="50%"
              gradientUnits="objectBoundingBox"
            >
              <stop offset="0%" stopColor={b.color} stopOpacity="0.92" />
              <stop offset="40%" stopColor={b.color} stopOpacity="0.58" />
              <stop offset="72%" stopColor={b.color} stopOpacity="0.22" />
              <stop offset="100%" stopColor={b.color} stopOpacity="0" />
            </radialGradient>
          ))}
        </defs>

        <g style={{ mixBlendMode: 'screen' }}>
          {blobs.map((b) => (
            <ellipse
              key={`blob-${uid}-${b.id}`}
              cx={b.cx}
              cy={b.cy}
              rx={b.rx}
              ry={b.ry}
              fill={`url(#grad-${uid}-${b.id})`}
            />
          ))}
        </g>
      </svg>

      {zones.length === 0 && (
        <div className="absolute bottom-3 left-3 rounded-md border border-white/10 bg-black/60 px-2.5 py-1 text-[10px] text-muted-foreground backdrop-blur-sm">
          No zones configured for this camera
        </div>
      )}

      <div className="absolute top-3 right-3 flex items-center gap-1.5 rounded-full bg-black/60 px-2.5 py-1 backdrop-blur-sm border border-white/10">
        <span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse" />
        <span className="text-[10px] font-medium tracking-wider text-green-400 uppercase">Live</span>
      </div>

      {snapshotHint && <SnapshotPreviewHint kind={snapshotHint} />}
    </div>
  );
}

