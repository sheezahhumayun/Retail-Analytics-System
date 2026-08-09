'use client';

import type { SnapshotHintKind } from '@/lib/snapshot-preview-hint';
import { SNAPSHOT_HINT_MESSAGES } from '@/lib/snapshot-preview-hint';

interface SnapshotPreviewHintProps {
  kind: SnapshotHintKind;
}

/** Small overlay badge — must not block canvas interaction underneath. */
export function SnapshotPreviewHint({ kind }: SnapshotPreviewHintProps) {
  return (
    <div
      className="pointer-events-none absolute bottom-3 left-1/2 z-10 max-w-[90%] -translate-x-1/2 rounded-full border border-white/10 bg-black/60 px-3 py-1.5 text-center text-xs text-muted-foreground backdrop-blur-sm"
      role="status"
    >
      {SNAPSHOT_HINT_MESSAGES[kind]}
    </div>
  );
}
