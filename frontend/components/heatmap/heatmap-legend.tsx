import { heatGradientCss } from "@/lib/heatmap-colors";

export function HeatmapLegend() {
  return (
    <div className="flex items-center gap-4 rounded-xl border border-border bg-card px-5 py-3.5">
      <span className="shrink-0 text-xs font-medium text-muted-foreground tracking-wide uppercase">
        Heat Scale
      </span>

      <div className="flex flex-1 items-center gap-2">
        <span className="shrink-0 text-[11px] text-muted-foreground">Low</span>
        <div
          className="h-3 flex-1 rounded-md border border-white/10"
          style={{ background: heatGradientCss("to right") }}
          role="img"
          aria-label="Heat intensity gradient from low to high"
        />
        <span className="shrink-0 text-[11px] text-muted-foreground">High</span>
      </div>
    </div>
  );
}
