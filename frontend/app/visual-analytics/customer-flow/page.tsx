'use client';

import { useEffect, useMemo, useState } from 'react';
import { DashboardShell } from '@/components/dashboard/dashboard-shell';
import { ScopeContextBanner } from '@/components/dashboard/scope-context-banner';
import { CustomerFlowControls } from '@/components/customer-flow/customer-flow-controls';
import { CustomerFlowViz } from '@/components/customer-flow/customer-flow-viz';
import { FutureFeatureCallout } from '@/components/customer-flow/future-feature-callout';
import {
  filterCustomerFlowCameras,
  resolveCustomerFlowCameraId,
} from '@/lib/scope/scope-filters';
import { useScope } from '@/lib/scope/ScopeContext';

export default function CustomerFlowPage() {
  const { store, cameraId, storeCameraIds } = useScope();
  const [pageCamera, setPageCamera] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const storeCameras = useMemo(
    () => store?.cameras.map((camera) => ({ id: camera.id, label: camera.name })) ?? [],
    [store],
  );

  const allowedCameras = useMemo(
    () => filterCustomerFlowCameras(storeCameras, cameraId, storeCameraIds),
    [storeCameras, cameraId, storeCameraIds],
  );

  const allowedCameraIds = useMemo(
    () => allowedCameras.map((camera) => camera.id),
    [allowedCameras],
  );

  const effectiveCamera = useMemo(
    () =>
      resolveCustomerFlowCameraId(
        cameraId,
        pageCamera || (allowedCameraIds[0] ?? ''),
        allowedCameraIds,
      ),
    [cameraId, pageCamera, allowedCameraIds],
  );

  useEffect(() => {
    if (allowedCameraIds.length > 0 && !allowedCameraIds.includes(pageCamera)) {
      setPageCamera(effectiveCamera);
    }
  }, [allowedCameraIds, pageCamera, effectiveCamera]);

  return (
    <DashboardShell>
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Customer Flow</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Visualize common walking patterns and movement routes through your store
          </p>
        </div>

        <ScopeContextBanner />

        <CustomerFlowControls
          cameras={allowedCameras}
          selectedCamera={effectiveCamera}
          onCameraChange={setPageCamera}
          date={date}
          onDateChange={setDate}
        />

        <CustomerFlowViz cameraId={effectiveCamera} />

        <FutureFeatureCallout />
      </div>
    </DashboardShell>
  );
}
