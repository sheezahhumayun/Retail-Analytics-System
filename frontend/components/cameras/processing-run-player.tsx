"use client"

import type { CountingLine, OverlayState, Zone } from "@/lib/types"

/** Same 16:9 coordinate space as CameraFrame. */
const SX = 1.6
const SY = 0.9

const ZONE_COLORS: Record<Zone["variant"], string> = {
  accent: "236 72 153",
  warm: "245 158 11",
  cool: "20 184 166",
}

const LINE_COLOR = "37 99 235"

function scalePoints(points: string): string {
  return points
    .split(" ")
    .map((pair) => {
      const [x, y] = pair.split(",").map(Number)
      return `${x * SX},${y * SY}`
    })
    .join(" ")
}

function centroid(points: string): { x: number; y: number } {
  const coords = points.split(" ").map((p) => p.split(",").map(Number))
  const x = coords.reduce((s, c) => s + c[0], 0) / coords.length
  const y = coords.reduce((s, c) => s + c[1], 0) / coords.length
  return { x: x * SX, y: y * SY }
}

export function ProcessingRunPlayer({
  videoUrl,
  zones,
  countingLines,
  overlays,
  playerId = "processing-run",
}: {
  videoUrl: string
  zones: Zone[]
  countingLines: CountingLine[]
  overlays: OverlayState
  playerId?: string
}) {
  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-md bg-muted">
      <video
        src={videoUrl}
        controls
        className="h-full w-full object-cover"
        playsInline
      />

      <svg
        viewBox="0 0 160 90"
        className="pointer-events-none absolute inset-0 h-full w-full"
        aria-hidden="true"
      >
        <defs>
          <marker
            id={`arrow-${playerId}`}
            viewBox="0 0 10 10"
            refX="8"
            refY="5"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill={`rgb(${LINE_COLOR})`} />
          </marker>
        </defs>

        {overlays.zones &&
          zones.map((zone) => {
            const c = centroid(zone.points)
            const color = ZONE_COLORS[zone.variant]
            return (
              <g key={zone.id}>
                <polygon
                  points={scalePoints(zone.points)}
                  fill={`rgb(${color} / 0.16)`}
                  stroke={`rgb(${color})`}
                  strokeWidth={0.6}
                  strokeDasharray="2 1.5"
                />
                <text
                  x={c.x}
                  y={c.y}
                  textAnchor="middle"
                  fontSize={3.4}
                  fontWeight={600}
                  fill={`rgb(${color})`}
                >
                  {zone.label}
                </text>
              </g>
            )
          })}

        {overlays.countingLines &&
          countingLines.map((line) => (
            <g key={line.id}>
              <line
                x1={line.x1 * SX}
                y1={line.y1 * SY}
                x2={line.x2 * SX}
                y2={line.y2 * SY}
                stroke={`rgb(${LINE_COLOR})`}
                strokeWidth={0.8}
                markerEnd={`url(#arrow-${playerId})`}
              />
              <text
                x={line.x1 * SX + 1.5}
                y={line.y1 * SY + 3.5}
                fontSize={3.2}
                fontWeight={600}
                fill={`rgb(${LINE_COLOR})`}
              >
                {line.label}
              </text>
            </g>
          ))}
      </svg>
    </div>
  )
}
