"use client"

import { Box, Hash, Shapes, Minus } from "lucide-react"

import type { OverlayState } from "@/lib/types"

export const DEFAULT_OVERLAYS: OverlayState = {
  boundingBoxes: true,
  trackIds: true,
  zones: true,
  countingLines: true,
}

/** Live camera preview (Phase 1a): zones/lines only — no inference overlays yet. */
export const LIVE_CAMERA_OVERLAYS: OverlayState = {
  boundingBoxes: false,
  trackIds: false,
  zones: true,
  countingLines: true,
}

type ToggleKey = keyof OverlayState

const TOGGLES: { key: ToggleKey; label: string; icon: typeof Box }[] = [
  { key: "boundingBoxes", label: "Bounding Boxes", icon: Box },
  { key: "trackIds", label: "Track IDs", icon: Hash },
  { key: "zones", label: "Zones", icon: Shapes },
  { key: "countingLines", label: "Counting Lines", icon: Minus },
]

const LIVE_CAMERA_TOGGLE_KEYS = new Set<ToggleKey>(["zones", "countingLines"])

export function OverlayToggles({
  value,
  onChange,
  size = "sm",
  mode = "full",
}: {
  value: OverlayState
  onChange: (next: OverlayState) => void
  size?: "sm" | "md"
  /** `live` hides bounding-box / track-ID toggles (no inference overlay yet). */
  mode?: "full" | "live"
}) {
  const toggles =
    mode === "live"
      ? TOGGLES.filter(({ key }) => LIVE_CAMERA_TOGGLE_KEYS.has(key))
      : TOGGLES

  return (
    <div className="flex flex-wrap gap-1.5">
      {toggles.map(({ key, label, icon: Icon }) => {
        const active = value[key]
        return (
          <button
            key={key}
            type="button"
            aria-pressed={active}
            onClick={() => onChange({ ...value, [key]: !active })}
            className={`inline-flex items-center gap-1.5 rounded-full border font-medium transition-colors ${
              size === "md" ? "px-3 py-1.5 text-sm" : "px-2.5 py-1 text-xs"
            } ${
              active
                ? "border-primary bg-primary/10 text-primary"
                : "border-border bg-transparent text-muted-foreground hover:bg-muted"
            }`}
          >
            <Icon className={size === "md" ? "h-4 w-4" : "h-3.5 w-3.5"} />
            {label}
          </button>
        )
      })}
    </div>
  )
}
