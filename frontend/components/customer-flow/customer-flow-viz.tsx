'use client';

interface CustomerFlowVizProps {
  cameraId: string;
}

export function CustomerFlowViz({ cameraId: _cameraId }: CustomerFlowVizProps) {
  return (
    <div className="rounded-xl border border-dashed border-border bg-card/40 overflow-hidden">
      <div className="flex flex-col items-center justify-center gap-3 px-6 py-20 text-center">
        <p className="text-lg font-semibold text-foreground">Customer flow analytics not available yet</p>
        <p className="max-w-lg text-sm text-muted-foreground">
          {/* TODO: no backend endpoint yet - see PROJECT_STATUS.md */}
          Path sequencing and route analytics require a backend customer-flow API. This page will
          show real trajectory data once that endpoint exists.
        </p>
      </div>
    </div>
  );
}
