"use client"

import { useState } from "react"
import { Maximize2 } from "lucide-react"

import type { Camera, OverlayState } from "@/lib/types"
import {
  LIVE_CAMERA_OVERLAYS,
  OverlayToggles,
} from "@/components/cameras/overlay-toggles"
import { CameraFrame } from "@/components/cameras/camera-frame"
import { CameraModal } from "@/components/cameras/camera-modal"
import { StatusBadge } from "@/components/cameras/status-badge"

export function CameraTile({ camera }: { camera: Camera }) {
  const [overlays, setOverlays] = useState<OverlayState>(LIVE_CAMERA_OVERLAYS)
  const [expanded, setExpanded] = useState(false)

  return (
    <>
      <div className="flex flex-col rounded-lg border border-border bg-card p-4">
        {/* Header: name + status */}
        <div className="mb-3 flex items-start justify-between gap-2">
          <div>
            <h3 className="text-sm font-semibold text-foreground">{camera.name}</h3>
            <p className="text-xs text-muted-foreground">{camera.location}</p>
          </div>
          <StatusBadge status={camera.status} />
        </div>

        {/* Overlay toggles above the tile */}
        <div className="mb-2.5">
          <OverlayToggles value={overlays} onChange={setOverlays} mode="live" />
        </div>

        {/* Clickable frame -> expands to modal */}
        <button
          type="button"
          onClick={() => setExpanded(true)}
          aria-label={`Expand ${camera.name}`}
          className="group relative block w-full rounded-md focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <CameraFrame camera={camera} overlays={overlays} />
          <span className="absolute right-2 top-2 flex h-7 w-7 items-center justify-center rounded-md bg-background/80 text-foreground opacity-0 backdrop-blur transition-opacity group-hover:opacity-100">
            <Maximize2 className="h-3.5 w-3.5" />
          </span>
        </button>
      </div>

      {expanded && (
        <CameraModal
          camera={camera}
          overlays={overlays}
          onOverlaysChange={setOverlays}
          onClose={() => setExpanded(false)}
        />
      )}
    </>
  )
}
