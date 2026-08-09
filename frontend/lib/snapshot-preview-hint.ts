import type { CameraSourceType, CameraStatus } from '@/lib/types';

export type SnapshotHintKind = 'source_unavailable' | 'process_first';

export const SNAPSHOT_HINT_MESSAGES: Record<SnapshotHintKind, string> = {
  source_unavailable: 'Camera source unavailable',
  process_first: 'Process this camera to see a real camera view here.',
};

/** Decide which non-blocking hint to show when a snapshot could not be loaded. */
export function resolveSnapshotHint(
  cameraStatus: CameraStatus | undefined,
  sourceType: CameraSourceType | undefined,
  snapshotUnavailable: boolean,
): SnapshotHintKind | null {
  if (!snapshotUnavailable) return null;
  if (cameraStatus === 'error') return 'source_unavailable';
  if (sourceType === 'recorded' && cameraStatus === 'online') return 'process_first';
  return null;
}
